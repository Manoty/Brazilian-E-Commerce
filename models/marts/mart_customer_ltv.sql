with orders as (
    select * from {{ ref('fct_orders') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

order_summary as (
    select
        customer_id,
        count(distinct order_id)            as total_orders,
        sum(total_payment_value)            as total_spent,
        avg(total_payment_value)            as avg_order_value,
        min(ordered_at)                     as first_order_at,
        max(ordered_at)                     as last_order_at,
        avg(avg_review_score)               as avg_review_score,
        datediff(
            'day', min(ordered_at), max(ordered_at)
        )                                   as customer_lifespan_days
    from orders
    where order_status = 'delivered'
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_unique_id,
        c.city,
        c.state,
        o.total_orders,
        o.total_spent,
        o.avg_order_value,
        o.first_order_at,
        o.last_order_at,
        o.customer_lifespan_days,
        o.avg_review_score,

        -- LTV segment
        case
            when o.total_spent >= 1000  then 'high_value'
            when o.total_spent >= 300   then 'mid_value'
            else                             'low_value'
        end                                 as ltv_segment
    from customers c
    inner join order_summary o on c.customer_id = o.customer_id
)

select * from final