-- * Project Name: BONDVAULT PK
-- * Description: SQL Schema for admins table.
-- * Author: Wolf4605
-- * Email: mab4605@gmail.com
-- * Date: 2026-10-22 08:22:39
-- * Last Modified by:   Wolf4605
-- * Last Modified time: 2026-10-23 06:01:30
-- * License: MIT
-- * Copyright© BondVault PK. All rights reserved.
CREATE TABLE IF NOT EXISTS "admins"(
    "id" UUID PRIMARY KEY DEFAULT UUIDV7(),
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "first_name" VARCHAR(100),
    "last_name" VARCHAR(100),
    "contact" VARCHAR(20),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_superuser" BOOLEAN NOT NULL DEFAULT FALSE
);

