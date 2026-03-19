with customers as (
    select * from {{ ref('stg_customers') }}
),

geolocation as (
    select
        zip_code_prefix,
        avg(latitude)   as latitude,
        avg(longitude)  as longitude
    from {{ ref('stg_geolocation') }}
    group by zip_code_prefix
),

final as (
    select
        c.customer_id,
        c.customer_unique_id,
        c.zip_code_prefix,
        c.city,
        c.state,
        g.latitude,
        g.longitude
    from customers c
    left join geolocation g
        on c.zip_code_prefix = g.zip_code_prefix
)

select * from final