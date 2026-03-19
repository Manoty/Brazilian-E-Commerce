with order_items as (
    select * from {{ ref('fct_order_items') }}
),

sellers as (
    select * from {{ ref('dim_sellers') }}
),

seller_summary as (
    select
        seller_id,
        count(distinct order_id)                        as total_orders,
        count(order_item_id)                            as total_items_sold,
        sum(price)                                      as total_revenue,
        avg(price)                                      as avg_item_price,
        avg(freight_value)                              as avg_freight_value,
        sum(case when is_late_delivery then 1 else 0 end) as late_deliveries,
        round(
            sum(case when is_late_delivery then 1 else 0 end) * 100.0
            / nullif(count(distinct order_id), 0), 2
        )                                               as late_delivery_rate_pct,
        count(distinct category_name_english)           as unique_categories
    from order_items
    group by seller_id
),

final as (
    select
        s.seller_id,
        s.city          as seller_city,
        s.state         as seller_state,
        ss.total_orders,
        ss.total_items_sold,
        ss.total_revenue,
        ss.avg_item_price,
        ss.avg_freight_value,
        ss.late_deliveries,
        ss.late_delivery_rate_pct,
        ss.unique_categories,

        -- performance tier
        case
            when ss.total_revenue >= 50000  then 'top_seller'
            when ss.total_revenue >= 10000  then 'mid_seller'
            else                                 'low_seller'
        end                                     as seller_tier
    from sellers s
    inner join seller_summary ss on s.seller_id = ss.seller_id
)

select * from final