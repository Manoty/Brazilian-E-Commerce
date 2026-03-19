with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select
        order_id,
        sum(payment_value)              as total_payment_value,
        count(payment_sequential)       as payment_count,
        max(payment_installments)       as max_installments
    from {{ ref('stg_payments') }}
    group by order_id
),

reviews as (
    select
        order_id,
        avg(review_score)               as avg_review_score
    from {{ ref('stg_reviews') }}
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.order_status,
        o.ordered_at,
        o.approved_at,
        o.shipped_at,
        o.delivered_at,
        o.estimated_delivery_at,

        -- delivery metrics
        datediff('day', o.ordered_at, o.delivered_at)           as days_to_deliver,
        datediff('day', o.ordered_at, o.estimated_delivery_at)  as days_estimated,
        case
            when o.delivered_at > o.estimated_delivery_at then true
            else false
        end                                                      as is_late_delivery,

        -- payment metrics
        p.total_payment_value,
        p.payment_count,
        p.max_installments,

        -- review
        r.avg_review_score

    from orders o
    left join payments p on o.order_id = p.order_id
    left join reviews r  on o.order_id = r.order_id
)

select * from final