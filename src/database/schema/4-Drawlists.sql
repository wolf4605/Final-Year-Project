-- * Project Name: BONDVAULT PK
-- * Description: SQL SCHEMA FOR drawlists Table
-- * Author: Wolf4605
-- * Email: mab4605@gmail.com
-- * Date: 2026-10-22 09:40:26
-- * Last Modified by:   Wolf4605
-- * Last Modified time: 2026-10-22 10:08:03
-- * License: MIT
-- * Copyright© BondVault PK. All rights reserved.
CREATE TABLE IF NOT EXISTS "drawlists"(
    "draw_date" TIMESTAMPTZ NOT NULL,
    "denomination" INT NOT NULL CHECK ("denomination" IN (100, 200, 750, 1500, 25000, 40000)),
    "first_winner" VARCHAR,
    "first_prize" INT,
    "second_winner" VARCHAR[],
    "second_prize" INT,
    "other_winners" VARCHAR[],
    "other_prize" INT,
    PRIMARY KEY ("draw_date", "denomination")
);

