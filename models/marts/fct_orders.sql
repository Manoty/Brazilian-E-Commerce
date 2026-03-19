with orders_enriched as (
    select * from {{ ref('int_orders_enriched') }}
),

final as (
    select
        order_id,
        customer_id,
        order_status,
        ordered_at,
        approved_at,
        shipped_at,
        delivered_at,
        estimated_delivery_at,
        total_payment_value,
        payment_count,
        max_installments,
        avg_review_score,

        -- delivery metrics
        datediff('day', ordered_at, delivered_at)           as days_to_deliver,
        datediff('day', ordered_at, estimated_delivery_at)  as days_estimated,
        case
            when delivered_at > estimated_delivery_at then true
            else false
        end                                                  as is_late_delivery

    from orders_enriched
)

select * from final