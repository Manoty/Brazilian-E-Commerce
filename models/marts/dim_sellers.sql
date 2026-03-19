with sellers as (
    select * from {{ ref('stg_sellers') }}
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
        s.seller_id,
        s.zip_code_prefix,
        s.city,
        s.state,
        g.latitude,
        g.longitude
    from sellers s
    left join geolocation g
        on s.zip_code_prefix = g.zip_code_prefix
)

select * from final