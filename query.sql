SELECT "order_order"."id",
       (SELECT order_orderstatus."status"
        FROM "order_orderstatus"
        WHERE order_orderstatus."order_id" = ("order_order"."id")
        ORDER BY order_orderstatus."created" DESC
        LIMIT 1) AS "latest_status"
FROM "order_order"
WHERE latest_status = 'canceled'