-- * Project Name: BONDVAULT PK
-- * Description: SQL Schema for reports table.
-- * Author: Wolf4605
-- * Email: mab4605@gmail.com
-- * Date: 2026-10-22 09:42:07
-- * Last Modified by:   Wolf4605
-- * Last Modified time: 2026-10-23 06:02:01
-- * License: MIT
-- * Copyright© BondVault PK. All rights reserved.
CREATE TABLE IF NOT EXISTS "reports"(
    "id" UUID PRIMARY KEY DEFAULT UUIDV7(),
    "reported_by" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "subject" VARCHAR(200) NOT NULL,
    "content" TEXT NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK ("status" IN ('pending', 'resolved')),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolved_at" TIMESTAMPTZ,
    "resolved_by" UUID REFERENCES "admins"("id") ON DELETE SET NULL,
    "response" TEXT,
    CONSTRAINT resolved_report_data_valid CHECK (("status" = 'pending' AND "resolved_at" IS NULL) OR ("status" = 'resolved' AND "resolved_at" IS NOT NULL))
);
