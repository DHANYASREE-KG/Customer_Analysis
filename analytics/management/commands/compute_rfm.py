import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.db import connection
from analytics.models import Customer, Order, RfmSegment


def percentile_score(series: pd.Series, n_bins: int = 4, invert: bool = False) -> pd.Series:
    percentiles = np.percentile(series.values, np.linspace(0, 100, n_bins + 1))
    percentiles = np.unique(percentiles)
    labels = list(range(1, len(percentiles)))
    if invert:
        labels = labels[::-1]
    return pd.cut(series, bins=percentiles, labels=labels,
                  include_lowest=True).astype(int)


def assign_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 3 and f >= 3 and m >= 3:
        return "Champion"
    elif r >= 3 and f >= 2:
        return "Loyal"
    elif r >= 2 and m >= 2:
        return "Potential Loyalist"
    elif r >= 2:
        return "At Risk"
    elif f >= 2:
        return "Need Attention"
    return "Lost"


class Command(BaseCommand):
    help = "Compute RFM segmentation from Order data and save to database"

    def handle(self, *args, **options):
        self.stdout.write("Loading orders from database...")

        orders = Order.objects.values(
            "customer_id", "order_date", "sales",
        )
        df = pd.DataFrame(list(orders))

        self.stdout.write(f"  Orders loaded: {len(df):,}")

        if df.empty:
            self.stdout.write(self.style.ERROR("No orders found. Run import_data first."))
            return

        df["order_date"] = pd.to_datetime(df["order_date"])
        reference_date = df["order_date"].max() + pd.Timedelta(days=1)

        self.stdout.write("  Computing RFM metrics...")
        rfm = df.groupby("customer_id").agg(
            Recency=("order_date", lambda x: (reference_date - x.max()).days),
            Frequency=("customer_id", "count"),
            Monetary=("sales", "sum"),
        ).reset_index()

        self.stdout.write(f"  Unique customers: {len(rfm):,}")

        self.stdout.write("  Scoring...")
        rfm["R_Score"] = percentile_score(rfm["Recency"], invert=True)
        rfm["F_Score"] = percentile_score(rfm["Frequency"])
        rfm["M_Score"] = percentile_score(rfm["Monetary"])
        rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

        self.stdout.write("  Assigning segments...")
        rfm["Segment"] = rfm.apply(assign_segment, axis=1)

        seg_summary = (
            rfm.groupby("Segment")
            .agg(
                Customers=("customer_id", "count"),
                Avg_Monetary=("Monetary", "mean"),
            )
            .round(1)
        )
        for seg, row in seg_summary.iterrows():
            self.stdout.write(f"    {seg:20s}  {int(row['Customers']):4d} customers  ₹{row['Avg_Monetary']:,.0f} avg")

        self.stdout.write("  Saving to database...")
        RfmSegment.objects.all().delete()

        objs = []
        for _, row in rfm.iterrows():
            objs.append(RfmSegment(
                customer_id=row["customer_id"],
                recency=int(row["Recency"]),
                frequency=int(row["Frequency"]),
                monetary=round(row["Monetary"], 2),
                r_score=int(row["R_Score"]),
                f_score=int(row["F_Score"]),
                m_score=int(row["M_Score"]),
                rfm_score=int(row["RFM_Score"]),
                segment=row["Segment"],
            ))

        RfmSegment.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS(
            f"Done! {len(objs):,} RFM segments saved to database."
        ))
