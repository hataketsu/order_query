# Challenge
1. Take the following example schema:
 
   - Model: Order
     - Field: ID
   - Model: OrderStatus
     - Field: ID
     - Field: Created (DateTime)
     - Field: Status (Text: Pending/Complete/Cancelled)
     - Field: OrderID (ForeignKey)
 
2. We have a database of many Orders, and each Order has one or many OrderStatus records. Each OrderStatus row has columns for created datetime and a status of Pending/Complete/Failed. The status of every Order in the database is dictated by the most recent OrderStatus. A `Pending` OrderStatus will be created for an Order when it is first created, `Complete` OrderStatus is created after successful payment or `Cancelled` is created if payment fails, or also if a `Complete` Order is refunded it is also given status `Cancelled`.

3. Using the Django ORM, how would you structure a query to list all `Cancelled` orders in the database without changes to the schema. Given that the database may contain millions of Orders, what optimisations would you suggest to make through the use of other query techniques, technologies or schema changes to reduce burden on the database resources and improve response times.

4. Please use Django / Python for your solution. The logic and thought process demonstrated are the most important considerations rather than truly functional code, however code presentation is important as well as the technical aspect. If you cannot settle on a single perfect solution, you may also discuss alternative solutions to demonstrate your understanding of potential trade-offs as you encounter them. Of course if you consider a solution is too time consuming you are also welcome to clarify or elaborate on potential improvements or multiple solution approaches conceptually to demonstrate understanding and planned solution.

# Solution
### 1. Django ORM query to list all `Cancelled` orders in the database
```python
class OrderManager(models.Manager):
    def canceled(self):
        return self.annotate(
            latest_status=models.Subquery(OrderStatus.objects.filter(
                order=models.OuterRef('pk')
            ).order_by('-created').values('status')[:1])
        ).filter(latest_status=OrderStatus.Status.CANCELED)
```

```postgresql
SELECT "order_order"."id",
       (SELECT order_orderstatus."status"
        FROM "order_orderstatus"
        WHERE order_orderstatus."order_id" = ("order_order"."id")
        ORDER BY order_orderstatus."created" DESC
        LIMIT 1) AS "latest_status"
FROM "order_order"
WHERE latest_status = 'canceled';
```

#### Thought process:
- At first I thought about using `group by order_id` to group the order statuses by order and then use `Max(created)` to query only latest order statuses, then get list of `order_status_id` out, filter those IDs with `order_orderstatus.status = 'canceled'`, get all the `order_id` from results, then so I will get the list of needed orders. But it is not easy to get order status ID from Max, it requires special query like `CTE` or `ROW_NUMBER` and not supported by Django ORM. But this is the better query without changing the schema.
- Then I thought about using `annotate` to add a new field `latest_status` to the `Order` model. This field is a subquery that returns the latest status of the order. Then I use `filter` to filter the orders by the latest status. The query is not very efficient because it uses a subquery. With millions of orders, this query will be very slow since it will have to run the subquery for each order.


### 2. Optimizations
#### 2.1. Add `latest_status` field to `Order` model
```python
class Order(models.Model):
    ...
    latest_status = models.CharField(max_length=20, null=True, blank=True)
```

When a new `OrderStatus` is created, update the `latest_status` field of the `Order` model. This way, we don't have to run the subquery for each order when we want to get the latest status of the order. This will make the query in step 1 much faster.
For convenience, we can use `post_save` signal to update the `latest_status` field of the `Order` model when a new `OrderStatus` is created, updated or deleted.


```python
@receiver([post_delete, post_save], sender=OrderStatus)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    last_status = order.orderstatus_set.order_by('-created').first()
    if last_status:
        order.latest_status = last_status.status
    else:
        order.latest_status = instance.status
    order.save()
```
The updated version of code is in `improve_performance` branch.

#### 2.2. Indexes
- Add index to `OrderStatus.order` field
- Add index to `OrderStatus.created` field
- Add index to `OrderStatus.status` field
- Add index to `Order.latest_status` field

#### 2.3 Trade-offs
- Add `latest_status` field to `Order` model will make the code more complex and harder to maintain. We have to make sure that the `latest_status` field is always up to date with the latest status of the order. We can use `post_save` signal to update the `latest_status` field when a new `OrderStatus` is created, updated or deleted. But if we update the `OrderStatus` model in other ways, we have to make sure that the `latest_status` field is updated as well.
