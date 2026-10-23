-- * Project Name: BONDVAULT PK
-- * Description: SQL Schema for Bonlists and Bonds Table
-- * Author: Wolf4605
-- * Email: mab4605@gmail.com
-- * Date: 2026-10-22 09:38:49
-- * Last Modified by:   Wolf4605
-- * Last Modified time: 2026-10-23 06:01:14
-- * License: MIT
-- * Copyright© BondVault PK. All rights reserved.
CREATE TABLE IF NOT EXISTS "bondlists"(
    "id" UUID PRIMARY KEY DEFAULT UUIDV7(),
    "denomination" INT NOT NULL CHECK ("denomination" IN (100, 200, 750, 1500, 25000, 40000)),
    "user_id" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    CONSTRAINT "uq_user_denomination" UNIQUE ("user_id", "denomination")
);

CREATE TABLE IF NOT EXISTS "bonds"(
    "bondlist_id" UUID NOT NULL REFERENCES "bondlists"("id") ON DELETE CASCADE,
    "bond_number" VARCHAR(20) NOT NULL,
    PRIMARY KEY ("bondlist_id", "bond_number")
);
