with orders as (
    select * from {{ ref('fct_orders') }}
),

final as (
    select
        date_trunc('month', ordered_at)             as order_month,
        count(distinct order_id)                    as total_orders,
        count(distinct customer_id)                 as unique_customers,
        sum(total_payment_value)                    as total_revenue,
        avg(total_payment_value)                    as avg_order_value,
        sum(total_payment_value) / nullif(
            count(distinct customer_id), 0
        )                                           as revenue_per_customer
    from orders
    where order_status = 'delivered'
    group by date_trunc('month', ordered_at)
    order by order_month
)

select * from final