# Movement-module buying list — 8 motors

Snapshot date: **November 11, 2026**. Currency: **USD**. Quantities are purchase quantities.

- [Read the website tables](https://matthewma11.github.io/WebbSubmarineROV/resources/parts-to-buy.html)
- [Open the live Google Sheet](https://docs.google.com/spreadsheets/d/17dbXic_-cqCcyHlMcdPFjAtkF8hnMJh7JqnrQvZKGOg/edit?gid=820#gid=820)
- [Download the unchanged original Excel workbook](../../downloads/rov-movement-module-8-motors.xlsx)
- [Machine-readable snapshot](movement-module-2026-11-11.json)

The full list totals **$260.89 before tax and shipping**, or **$110.89 above the $150 cap**. The bench-test alternative budgets **$137.85 in parts plus a $12.15 reserve**, for **$150.00 total**.

Prices and notes below come from the source, including dated listing checks, allowances, unverified estimates, and reuse requirements. This publication does not recheck marketplace prices, confirm compatibility, or place orders. The live Sheet may change after this snapshot. Full original URLs are preserved in the Excel file and JSON snapshot; reader links to Amazon use the same product’s shorter `/dp/` URL.

## Movement Module

Movement only; 8 motors already owned ($0 new motor purchase), Pi and laptop reused. USD. Quantities are purchase quantities.

| Item | Unit price USD | Buy quantity | Line total USD | Product link | Price basis (source) | Notes |
| --- | ---: | ---: | ---: | --- | --- | --- |
| E-clip replacement set — 5 clips | $1.09 | 2 | $2.18 | [Product](https://www.altitudehobbies.com/products/replacement-e-clip-set-fits-suppo-2208-2212-series) | Verified seller price | 2 packs = 10 clips: 8 needed + 2 spares. Listed for Suppo 2212 / 3.17mm shafts; QWinOut fit NOT confirmed. Verify groove and clip thickness before ordering. |
| 5V 6A regulator | $32.00 | 1 | $32.00 | [Product](https://bluerobotics.com/store/comm-control-power/control/bec-5v6a-r1/) | Verified seller price | 7–26V input; use 3S candidate battery. Do not power Pi directly from battery. |
| 3S 5000–5200mAh LiPo, XT60 | $34.99 | 1 | $34.99 | [Product](https://zeeebattery.com/products/zeee-3s-lipo-battery-5200mah-11-1v-50c-xt60) | Displayed price; variant check | Seller displays US starting price $34.99; confirm XT60 single-pack variant at checkout. Confirm motor/ESC voltage and combined current before purchase. |
| 3S LiPo balance charger / leads | $46.69 | 1 | $46.69 | [Product](https://www.amazon.com/dp/B0FN6Q4RT8) | Live Amazon price | Live Amazon listing checked Oct 22: $46.69, seller Lotus Mall. Third-party Xiangtat-branded B6ACneo listing; authenticity not independently verified. AC cable listed; extensions may cost extra. |
| Gamepad | $19.99 | 1 | $19.99 | [Product](https://www.logitechg.com/en-us/shop/p/f310-gamepad.940-000110) | Verified seller price | Optional purchase: keyboard can be used; confirm laptop OS support. |
| Ethernet cable — 100 ft | $37.09 | 1 | $37.09 | [Product](https://www.monoprice.com/product?p_id=2119) | Verified seller price | Bench/prototype cable; not submarine-depth rated. Use existing short cable for bench test to save. |
| USB-to-Ethernet adapter | $8.90 | 1 | $8.90 | [Product](https://www.amazon.com/dp/B00YUU3KC6) | Unverified retained estimate | Buy only if laptop lacks Ethernet; USB-A connector. |
| Female-to-female jumper wire pack | $6.89 | 1 | $6.89 | [Product](https://www.amazon.com/dp/B07GD312VG) | Unverified retained estimate | Pi I2C, grounds and low-current signals only. |
| Pico H motor-control bridge + watchdog + USB cable | $10.00 | 1 | $10.00 | [Product](https://www.raspberrypi.com/products/raspberry-pi-pico/) | Budget allowance | Pi USB/UART commands → Pico generates 8 ESC signals (DShot where required). Custom bridge/watchdog firmware needed; test 3D reversing, arming and command-loss shutdown. Programming adapter/passthrough for ESC setup may cost extra. |
| Tecunite servo-extension cable pack — 20 leads | $8.99 | 2 | $17.98 | [Product](https://www.amazon.com/dp/B07C18BXDV) | Live Amazon pack price | $8.99 per 20-lead pack; buy quantity 2 = 40 leads for $17.98. 3-pin servo connectors do not directly fit 8-pin JST-SH ESC ports; actual ESC harness pinout still needs confirmation. |
| Matek PDB-HEX power distribution board | $26.40 | 1 | $26.40 | [Product](https://www.aliexpress.us/item/3256805956235938.html?src=google&src=google&albch=shopping&acnt=708-803-3821&isdl=y&slnk=&plac=&mtctp=&albbt=Google_7_shopping&aff_platform=google&aff_short_key=UneMJZVf&gclsrc=aw.ds&albagn=888888&ds_e_adid=&ds_e_matchtype=&ds_e_device=c&ds_e_network=x&ds_e_product_group_id=&ds_e_product_id=en3256805956235938&ds_e_product_merchant_id=5089697500&ds_e_product_country=US&ds_e_product_language=en&ds_e_product_channel=online&ds_e_product_store_id=&ds_url_v=2&albcp=19108282527&albag=&isSmbAutoCall=false&needSmbHouyi=false&gad_source=1&gad_campaignid=19108284222&gbraid=0AAAAAD6I-hHXQTTv1Gn2vSc6IFTBWy5uy&gclid=Cj0KCQjw6ObWBhDDARIsAFdfcUgvXr5ljpaj-N4DZ9_enBSA3FCZSjl8rNtkkyLswaqVDGhw7SbcyT4aAnuOEALw_wcB&gatewayAdapt=glo2usa) | Live new-shopper offer | Live AliExpress offer $26.40, new shoppers, max 1 per shopper. Struck-through $90.62 is not a confirmed returning-customer checkout price. Eligibility/tax may change total. |
| XT60 connector pigtail pack — 6 pieces | $9.98 | 1 | $9.98 | [Product](https://www.amazon.com/dp/B0DB1LBGSH) | Live Amazon pack price | Selected 12AWG-wire option, $9.98 for 6 XT60 pigtails, 100mm long. Additional long power wiring or motor connectors not included. |
| 40-pin 2.54mm male header strips | $1.95 | 4 | $7.80 | [Product](https://www.sparkfun.com/straight-header-male-pth-0-1in-40-pin.html) | Verified seller price | 4 strips = 160 pins. Signal connections only; not battery/ESC power. Replaces stale already-owned note because revised sheet requests 4 strips. |
| TOTAL BEFORE TAX / SHIPPING |  |  | $260.89 |  |  | Recalculated using checked listing prices plus remaining marked estimates. Tax/shipping/surcharges extra; PDB price assumes new-shopper eligibility. No purchase made. |
| Budget cap | $150.00 |  |  |  |  | Latest requested maximum. |
| Amount over budget |  |  | $110.89 |  |  | Total remains above $150; unverified marketplace prices may change. |

## Movement Budget 150

Requires reuse: Pi 4 + suitable 5V/3A USB-C supply, laptop, short Ethernet cable/interface, 8 motors, 2 compatible 4-in-1 ESCs, microSD and assembly supplies. Confirm availability before ordering.

| Item | Unit price USD | Buy quantity | Line total USD | Product link | Price basis (source) | Notes |
| --- | ---: | ---: | ---: | --- | --- | --- |
| E-clip set — 5 clips | $1.09 | 2 | $2.18 | [Product](https://www.altitudehobbies.com/products/replacement-e-clip-set-fits-suppo-2208-2212-series) | Checked listing | 10 clips total; QWinOut shaft-groove fit still unconfirmed. |
| 3S 5200mAh LiPo — XT60 | $34.99 | 1 | $34.99 | [Product](https://zeeebattery.com/products/zeee-3s-lipo-battery-5200mah-11-1v-50c-xt60) | Displayed starting price | Confirm US XT60 variant price, motor/ESC 3S support and total current. |
| B6ACneo-type AC balance charger | $46.69 | 1 | $46.69 | [Product](https://www.amazon.com/dp/B0FN6Q4RT8) | Live Amazon price | Third-party Xiangtat listing; authenticity not independently verified. Includes AC cord per listing. Existing battery leads must reach both ports. |
| Pico H + USB data cable | $10.00 | 1 | $10.00 | [Product](https://www.raspberrypi.com/products/raspberry-pi-pico/) | Combined allowance | Ready-made board. Custom 8-channel signal generator/watchdog firmware required; verify actual ESC input protocol and reversing. |
| Female-to-female jumper wire pack | $6.89 | 1 | $6.89 | [Product](https://www.amazon.com/dp/B07GD312VG) | Retained estimate | Signal/ground wiring only; not motor power. |
| 40-pin 2.54mm male headers | $1.95 | 4 | $7.80 | [Product](https://www.sparkfun.com/straight-header-male-pth-0-1in-40-pin.html) | Checked listing | 4 strips per your revised list; optional if all required headers are already installed. |
| XT60 12AWG pigtail pack — 6 pieces | $9.98 | 1 | $9.98 | [Product](https://www.amazon.com/dp/B0DB1LBGSH) | Live Amazon price | DIY soldered battery split to 2 ESCs. Use supplied ESC signal harnesses; preserve pinouts and sufficient wire gauge. |
| MIDI / AMI fuse holder | $6.32 | 1 | $6.32 | [Product](https://coachcontrols.com/index.php?main_page=product_info&products_id=88) | Checked listing | Main positive feed near battery. Fuse and ring terminals separate. |
| MIDI fuse | $3.00 | 1 | $3.00 | [Product](https://coachcontrols.com/index.php?main_page=product_info&products_id=88) | Allowance; holder link | Select actual fuse rating after load/current and wiring check; not based on ESC peak rating. |
| Power wire, ring terminals, signal breakout materials | $10.00 | 1 | $10.00 |  | Allowance; select after ESC model | DIY power harness replaces PDB. Use motor leads and JST-SH harnesses supplied with existing ESCs; no servo-extension pack required if supplied leads reach. |
| Keyboard control / existing short Ethernet | $0.00 | 0 | $0.00 |  | Required reuse | No gamepad, 100-ft cable or adapter purchase. Laptop must already have Ethernet or a suitable adapter. |
| Existing Pi USB-C power supply | $0.00 | 0 | $0.00 |  | Required reuse, not verified owned | Bench-test Pi separately from battery using suitable 5V/3A supply. No onboard regulator in this budget; required later for self-contained ROV. |
| Existing 8 motors + 2 four-in-one ESCs | $0.00 | 0 | $0.00 |  | Already owned | Confirm ESC models, 3S voltage and reversible firmware before battery use; do not assume DShot telemetry equals reverse thrust. |
| Existing microSD, ties, heat-shrink and crimps | $0.00 | 0 | $0.00 |  | Already owned | Reuse your confirmed supplies. |
| PARTS SUBTOTAL |  |  | $137.85 |  |  | USD; mixed checked prices and allowances. |
| Reserve for tax/shipping/price variation |  |  | $12.15 |  |  | Reserve is a cap, not a verified shipping quote. If checkout exceeds $150, do not order all items. |
| TOTAL BUDGET |  |  | $150.00 |  |  | $150 cap; parts availability, tax and shipping not guaranteed. |
| LIMITATIONS |  |  |  |  |  | Bench movement control only. Camera/sensors/sonar, waterproofing and standalone battery-powered Pi operation excluded. No custom controller PCB, but custom firmware/software and soldering are required. |
