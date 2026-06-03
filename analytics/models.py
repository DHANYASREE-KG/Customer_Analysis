from django.db import models


class Customer(models.Model):
    customer_id = models.CharField(max_length=20, primary_key=True)
    customer_name = models.CharField(max_length=100)
    segment = models.CharField(max_length=50)

    class Meta:
        ordering = ['customer_id']

    def __str__(self):
        return f"{self.customer_name} ({self.customer_id})"


class Order(models.Model):
    order_id = models.CharField(max_length=20, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField()
    ship_date = models.DateField()
    ship_mode = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)
    sales = models.FloatField()
    quantity = models.IntegerField()
    discount = models.FloatField()
    profit = models.FloatField()
    profit_margin_pct = models.FloatField(null=True, blank=True)
    delivery_days = models.IntegerField(null=True, blank=True)
    revenue_per_unit = models.FloatField(null=True, blank=True)
    clv_bucket = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"{self.order_id} - {self.customer.customer_name}"


class RfmSegment(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='rfm')
    recency = models.IntegerField()
    frequency = models.IntegerField()
    monetary = models.FloatField()
    r_score = models.IntegerField()
    f_score = models.IntegerField()
    m_score = models.IntegerField()
    rfm_score = models.IntegerField()
    segment = models.CharField(max_length=50)

    class Meta:
        ordering = ['-monetary']

    def __str__(self):
        return f"{self.customer.customer_id} - {self.segment}"
