-- This code assumes we have a PostgreSQL database setup with a table xxx_option_chain
-- where 'xxx' is the symbol name for the option chains and a 'range' table specifying
-- the ranges for prices to observe for a given spread width.

WITH verticals AS (
    SELECT
      c1.symbol || '-' || c2.symbol                           AS "spread_symbol",
      c1.expiration :: DATE - c1.quote_date :: DATE           AS "DTE",
      c1.option_type,
      :width as "width",
      ROUND((((c1.bid - c2.bid) :: numeric + (c1.ask - c2.ask) :: numeric) / 2), 2) AS "mark"
    FROM vxx_option_chain c1
      INNER JOIN vxx_option_chain c2 ON (c1.strike - :width) = (c2.strike) AND
                                        c1.expiration = c2.expiration AND
                                        c1.quote_date = c2.quote_date AND
                                        c1.root = c2.root AND
                                        c1.option_type = c2.option_type AND
                                        c1.option_type = 'p'

), selection_start AS (

    SELECT
      spread_symbol,
      name,
      "DTE",
      mark
    FROM verticals
      INNER JOIN range ON mark > range.min_value AND
                           mark <= range.max_value AND
                           range.width = verticals.width AND
                           "DTE" = 46

), selection_end AS (

    SELECT
      spread_symbol,
      "DTE",
      mark
    FROM verticals
    WHERE "DTE" = 0

), valid_symbols AS (

    SELECT
      selection_start.spread_symbol,
      selection_start.name,
      selection_start."DTE" AS "Start_DTE",
      selection_end."DTE"   AS "End_DTE"
    FROM selection_start
      INNER JOIN selection_end ON selection_start.spread_symbol = selection_end.spread_symbol

)

SELECT
  verticals.spread_symbol,
  valid_symbols.name,
  verticals."DTE",
  verticals.mark
FROM verticals
  INNER JOIN valid_symbols
    ON verticals."DTE" <= valid_symbols."Start_DTE" AND verticals."DTE" >= valid_symbols."End_DTE" AND
       valid_symbols.spread_symbol = verticals.spread_symbol
WHERE mark >= 0 AND mark <= 2



