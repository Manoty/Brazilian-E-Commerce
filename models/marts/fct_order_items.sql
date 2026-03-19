with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select
        order_id,
        order_status,
        ordered_at,
        delivered_at,
        is_late_delivery
    from {{ ref('fct_orders') }}
),

products as (
    select
        product_id,
        category_name_english
    from {{ ref('dim_products') }}
),

sellers as (
    select
        seller_id,
        city    as seller_city,
        state   as seller_state
    from {{ ref('dim_sellers') }}
),

final as (
    select
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        oi.seller_id,
        oi.shipping_limit_at,
        oi.price,
        oi.freight_value,
        oi.price + oi.freight_value                             as total_item_value,
        oi.freight_value / nullif(oi.price, 0) * 100           as freight_pct_of_price,

        -- order context
        o.order_status,
        o.ordered_at,
        o.delivered_at,
        o.is_late_delivery,

        -- product context
        p.category_name_english,

        -- seller context
        s.seller_city,
        s.seller_state

    from order_items oi
    left join orders o   on oi.order_id   = o.order_id
    left join products p on oi.product_id = p.product_id
    left join sellers s  on oi.seller_id  = s.seller_id
)

select * from final