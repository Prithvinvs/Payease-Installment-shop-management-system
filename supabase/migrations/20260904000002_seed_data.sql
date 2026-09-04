-- Supabase Migration: 20260904000002_seed_data.sql
-- Description: Seeds default roles, administrative users, and global settings

-- 1. Seed Default Roles
INSERT INTO public.roles (id, role_name, description, permissions)
VALUES 
    (1, 'Super Admin', 'Full system control, user management, and system settings rights.', '{"all": true}'::jsonb),
    (2, 'Admin', 'Shop owner permissions to manage customers, sales, inventory, and reports.', '{"manage_shop": true}'::jsonb),
    (3, 'Manager', 'Store manager permissions to approve credits and monitor operations.', '{"manage_inventory": true, "manage_sales": true}'::jsonb),
    (4, 'Staff', 'Front-counter staff permissions to record sales and collect payments.', '{"record_sales": true, "collect_payments": true}'::jsonb)
ON CONFLICT (id) DO UPDATE 
SET role_name = EXCLUDED.role_name, description = EXCLUDED.description, permissions = EXCLUDED.permissions;

-- Reset sequence for roles table
SELECT setval('roles_id_seq', (SELECT MAX(id) FROM public.roles));

-- 2. Seed Default Administrative Users (Password: Admin@123)
INSERT INTO public.users (id, uuid, full_name, username, email, phone, password_hash, role_id, status)
VALUES
    (1, gen_random_uuid()::text, 'System Super Admin', 'superadmin', 'superadmin@payease.com', '+919999999999', '$2b$12$9YQ1x6yeCyEMQq7Tdk/AlOO6p8Yj69vRsYFECCeMbIvpl0SeunbD2', 1, 'active'),
    (2, gen_random_uuid()::text, 'Shop Owner Admin', 'admin', 'admin@payease.com', '+918888888888', '$2b$12$9YQ1x6yeCyEMQq7Tdk/AlOO6p8Yj69vRsYFECCeMbIvpl0SeunbD2', 2, 'active'),
    (3, gen_random_uuid()::text, 'Counter Staff Cashier', 'staff', 'staff@payease.com', '+917777777777', '$2b$12$9YQ1x6yeCyEMQq7Tdk/AlOO6p8Yj69vRsYFECCeMbIvpl0SeunbD2', 4, 'active')
ON CONFLICT (id) DO UPDATE
SET username = EXCLUDED.username, email = EXCLUDED.email, password_hash = EXCLUDED.password_hash;

SELECT setval('users_id_seq', (SELECT MAX(id) FROM public.users));

-- 3. Seed Default Global Settings
INSERT INTO public.settings (key, value)
VALUES
    ('shop_name', 'PayEase Store'),
    ('shop_address', 'MG Road, Bangalore, India'),
    ('shop_phone', '+91 98765 43210'),
    ('shop_email', 'info@payease.com'),
    ('gst_number', '29AAAAA1111A1Z1'),
    ('currency', 'INR'),
    ('timezone', 'Asia/Kolkata'),
    ('date_format', '%d-%b-%Y'),
    ('invoice_prefix', 'INV-'),
    ('receipt_prefix', 'RCT-'),
    ('backup_schedule', 'daily'),
    ('theme', 'light')
ON CONFLICT (key) DO NOTHING;

-- 4. Seed Default Categories
INSERT INTO public.categories (id, category_code, name, description, status)
VALUES
    (gen_random_uuid(), 'CAT001', 'Mobile Phones', 'Smartphones and mobile devices', 'active'),
    (gen_random_uuid(), 'CAT002', 'Laptops & Computers', 'Laptops, desktop PCs, and tablets', 'active'),
    (gen_random_uuid(), 'CAT003', 'Home Appliances', 'Refrigerators, washing machines, TVs, and air conditioners', 'active'),
    (gen_random_uuid(), 'CAT004', 'Electronics', 'Audio equipment, wearables, and electronic gadgets', 'active'),
    (gen_random_uuid(), 'CAT005', 'Accessories', 'Chargers, cases, cables, and power banks', 'active'),
    (gen_random_uuid(), 'CAT006', 'General', 'Uncategorized products', 'active')
ON CONFLICT (category_code) DO NOTHING;

-- 5. Seed Default Brands
INSERT INTO public.brands (id, brand_name, description, status)
VALUES
    (gen_random_uuid(), 'Apple', 'iPhone, iPad, Mac and Apple accessories', 'active'),
    (gen_random_uuid(), 'Samsung', 'Galaxy smartphones, TVs, and home appliances', 'active'),
    (gen_random_uuid(), 'Sony', 'Televisions, audio systems, and gaming consoles', 'active'),
    (gen_random_uuid(), 'LG', 'Home appliances and displays', 'active'),
    (gen_random_uuid(), 'Dell', 'Laptops and computing solutions', 'active'),
    (gen_random_uuid(), 'HP', 'Laptops, desktops, and printers', 'active'),
    (gen_random_uuid(), 'Xiaomi', 'Smartphones, TV, and smart devices', 'active'),
    (gen_random_uuid(), 'OnePlus', 'Smartphones and audio gear', 'active'),
    (gen_random_uuid(), 'Generic', 'Unbranded or general consumer goods', 'active')
ON CONFLICT (brand_name) DO NOTHING;

