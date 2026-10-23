-- * Project Name: BONDVAULT PK
-- * Description: SQL Schema for market table.
-- * Author: Wolf4605
-- * Email: mab4605@gmail.com
-- * Date: 2026-10-22 09:41:14
-- * Last Modified by:   Wolf4605
-- * Last Modified time: 2026-10-23 06:01:54
-- * License: MIT
-- * Copyright© BondVault PK. All rights reserved.
CREATE TABLE IF NOT EXISTS "market"(
    "id" UUID PRIMARY KEY DEFAULT UUIDV7(),
    "posted_by" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "title" VARCHAR(150) NOT NULL,
    "description" TEXT,
    "price" BIGINT NOT NULL CHECK ("price" >= 0),
    "category" VARCHAR(10) NOT NULL CHECK ("category" IN ('buy', 'sell')),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
