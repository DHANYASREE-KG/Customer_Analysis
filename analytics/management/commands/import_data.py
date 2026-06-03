import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from analytics.models import Customer, Order, RfmSegment


RAW_PATH = "analytics/data/ecommerce.csv"


class Command(BaseCommand):
    help = "Import ecommerce CSV data into SQLite database"

    def handle(self, *args, **options):
        self.stdout.write("Loading CSV...")
        df = pd.read_csv(RAW_PATH)
        self.stdout.write(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")

        df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True)

        df.drop_duplicates(inplace=True)
        self.stdout.write(f"  After dedup: {len(df):,} rows")

        # -- Customers --
        customers = df[["Customer ID", "Customer Name", "Segment"]].drop_duplicates()
        customer_objs = [
            Customer(
                customer_id=row["Customer ID"],
                customer_name=row["Customer Name"],
                segment=row["Segment"],
            )
            for _, row in customers.iterrows()
        ]
        Customer.objects.bulk_create(customer_objs, ignore_conflicts=True)
        self.stdout.write(f"  Customers created: {Customer.objects.count():,}")

        # -- Feature engineering --
        df["Profit Margin %"] = np.where(
            df["Sales"] > 0, (df["Profit"] / df["Sales"]) * 100, 0
        ).round(2)
        df["Delivery Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
        df["Revenue per Unit"] = (df["Sales"] / df["Quantity"]).round(2)

        cltv = df.groupby("Customer ID")["Sales"].sum().reset_index(name="Total Sales")
        p33, p66 = np.percentile(cltv["Total Sales"], [33, 66])
        cltv["CLV Bucket"] = pd.cut(
            cltv["Total Sales"],
            bins=[-np.inf, p33, p66, np.inf],
            labels=["Low", "Mid", "High"],
        )
        df = df.merge(cltv[["Customer ID", "CLV Bucket"]], on="Customer ID", how="left")

        # -- Orders --
        order_objs = []
        for _, row in df.iterrows():
            order_objs.append(Order(
                order_id=row["Order ID"],
                customer_id=row["Customer ID"],
                order_date=row["Order Date"].date(),
                ship_date=row["Ship Date"].date(),
                ship_mode=row["Ship Mode"],
                state=row["State"],
                region=row["Region"],
                category=row["Category"],
                sub_category=row["Sub-Category"],
                sales=row["Sales"],
                quantity=row["Quantity"],
                discount=row["Discount"],
                profit=row["Profit"],
                profit_margin_pct=row["Profit Margin %"],
                delivery_days=row["Delivery Days"],
                revenue_per_unit=row["Revenue per Unit"],
                clv_bucket=row["CLV Bucket"],
            ))

        Order.objects.bulk_create(order_objs, ignore_conflicts=True)
        self.stdout.write(f"  Orders created: {Order.objects.count():,}")

        self.stdout.write(self.style.SUCCESS("Import complete!"))
