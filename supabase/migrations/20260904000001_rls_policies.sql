-- Supabase Migration: 20260904000001_rls_policies.sql
-- Description: Enables Row Level Security (RLS) and access policies

-- 1. Helper Function to Check Active Staff/Admin/Manager User
CREATE OR REPLACE FUNCTION public.is_staff_or_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM public.users u
        JOIN public.roles r ON u.role_id = r.id
        WHERE u.id = auth.uid()
          AND u.status = 'active'
          AND r.role_name IN ('Super Admin', 'Admin', 'Manager', 'Staff')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Enable RLS on All Tables
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_resets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inventory_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_ledgers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.instalment_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.instalment_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;

-- 3. Define RLS Policies for Staff/Admin Access
DROP POLICY IF EXISTS "Staff/Admin access on roles" ON public.roles;
CREATE POLICY "Staff/Admin access on roles" ON public.roles
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on users" ON public.users;
CREATE POLICY "Staff/Admin access on users" ON public.users
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on password_resets" ON public.password_resets;
CREATE POLICY "Staff/Admin access on password_resets" ON public.password_resets
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on categories" ON public.categories;
CREATE POLICY "Staff/Admin access on categories" ON public.categories
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on brands" ON public.brands;
CREATE POLICY "Staff/Admin access on brands" ON public.brands
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on products" ON public.products;
CREATE POLICY "Staff/Admin access on products" ON public.products
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on inventory_movements" ON public.inventory_movements;
CREATE POLICY "Staff/Admin access on inventory_movements" ON public.inventory_movements
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on customers" ON public.customers;
CREATE POLICY "Staff/Admin access on customers" ON public.customers
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on customer_ledgers" ON public.customer_ledgers;
CREATE POLICY "Staff/Admin access on customer_ledgers" ON public.customer_ledgers
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on sales" ON public.sales;
CREATE POLICY "Staff/Admin access on sales" ON public.sales
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on sale_items" ON public.sale_items;
CREATE POLICY "Staff/Admin access on sale_items" ON public.sale_items
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on instalment_plans" ON public.instalment_plans;
CREATE POLICY "Staff/Admin access on instalment_plans" ON public.instalment_plans
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on instalment_schedules" ON public.instalment_schedules;
CREATE POLICY "Staff/Admin access on instalment_schedules" ON public.instalment_schedules
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on payments" ON public.payments;
CREATE POLICY "Staff/Admin access on payments" ON public.payments
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on payment_receipts" ON public.payment_receipts;
CREATE POLICY "Staff/Admin access on payment_receipts" ON public.payment_receipts
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on audit_logs" ON public.audit_logs;
CREATE POLICY "Staff/Admin access on audit_logs" ON public.audit_logs
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());

DROP POLICY IF EXISTS "Staff/Admin access on settings" ON public.settings;
CREATE POLICY "Staff/Admin access on settings" ON public.settings
    FOR ALL TO authenticated
    USING (public.is_staff_or_admin())
    WITH CHECK (public.is_staff_or_admin());
