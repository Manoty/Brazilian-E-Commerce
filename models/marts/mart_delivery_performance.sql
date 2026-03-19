with order_items as (
    select * from {{ ref('fct_order_items') }}
),

customers as (
    select
        customer_id,
        state as customer_state
    from {{ ref('dim_customers') }}
),

orders as (
    select
        order_id,
        customer_id,
        days_to_deliver,
        days_estimated,
        is_late_delivery,
        order_status
    from {{ ref('fct_orders') }}
),

joined as (
    select
        o.order_id,
        c.customer_state,
        oi.seller_state,
        o.days_to_deliver,
        o.days_estimated,
        o.is_late_delivery
    from orders o
    left join customers c   on o.customer_id  = c.customer_id
    left join order_items oi on o.order_id    = oi.order_id
    where o.order_status = 'delivered'
),

final as (
    select
        customer_state,
        seller_state,
        count(distinct order_id)                        as total_orders,
        avg(days_to_deliver)                            as avg_days_to_deliver,
        avg(days_estimated)                             as avg_days_estimated,
        sum(case when is_late_delivery then 1 else 0 end) as late_orders,
        round(
            sum(case when is_late_delivery then 1 else 0 end) * 100.0
            / nullif(count(distinct order_id), 0), 2
        )                                               as late_delivery_rate_pct
    from joined
    group by customer_state, seller_state
    order by late_delivery_rate_pct desc
)

select * from final