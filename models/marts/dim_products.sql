with products as (
    select * from {{ ref('stg_products') }}
),

translations as (
    select * from {{ ref('stg_product_category_translations') }}
),

final as (
    select
        p.product_id,
        p.category_name                             as category_name_portuguese,
        coalesce(t.category_name_english, 'unknown') as category_name_english,
        p.product_name_length,
        p.product_description_length,
        p.photos_qty,
        p.weight_g,
        p.length_cm,
        p.height_cm,
        p.width_cm
    from products p
    left join translations t
        on p.category_name = t.product_category_name
)

select * from final