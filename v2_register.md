# Parmair V2 Registers

Rekisterityyppi: Holding Regs (Funktiokoodit 03, 06, 16)
Rekisterin arvo: Single = int16, Double = uint32 (LSW löytyy seuraavasta rekisteristä)

MinLimit ja MaxLimit arvot esitetty skaalattuna

## 1 SYSTEM SETTINGS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 3 | ACK_ALARMS | Hälytysten kuittaus (0=ODOTETAAN KUITTAUSTA, 1=OK/KUITTAA) | 1 SYSTEM SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 4 | ALARM_COUNT | Aktiivisten hälytysten määrä | 1 SYSTEM SETTINGS | 0 | 1 | 0 | 100 | | ReadOnly | FALSE |
| 9 | TIME_YEAR | Vuosi | 1 SYSTEM SETTINGS | 2023 | 1 | 2000 | 3000 | | ReadWrite | FALSE |
| 10 | TIME_MONTH | Kuukausi | 1 SYSTEM SETTINGS | 8 | 1 | 1 | 12 | | ReadWrite | FALSE |
| 11 | TIME_DAY | Päivä | 1 SYSTEM SETTINGS | 1 | 1 | 1 | 31 | | ReadWrite | FALSE |
| 12 | TIME_HOUR | Tunnit | 1 SYSTEM SETTINGS | 1 | 1 | 0 | 23 | | ReadWrite | FALSE |
| 13 | TIME_MIN | Minuutit | 1 SYSTEM SETTINGS | 1 | 1 | 0 | 59 | | ReadWrite | FALSE |
| 14 | MULTI_FW_VER | Multi24 firmware versio | 1 SYSTEM SETTINGS | 2.00 | 100 | 0.00 | 100.00 | | ReadOnly | FALSE |
| 15 | MULTI_SW_VER | Multi24 sovelluksen ohjelmaversio | 1 SYSTEM SETTINGS | 2.00 | 100 | 0.00 | 100.00 | | ReadOnly | FALSE |
| 16 | MULTI_BL_VER | Multi24 bootloaderin ohjelmaversio | 1 SYSTEM SETTINGS | 2.00 | 100 | 0.00 | 100.00 | | ReadOnly | FALSE |

## 2 PHYSICAL INPUTS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 20 | TE01_M | Lämpötilamittaus, raitisilma | 2 PHYSICAL INPUTS | 0.0 | 10 | -50.0 | 120.0 | °C | ReadWrite | FALSE |
| 21 | TE05_M | Lämpötilamittaus, LTO kylmäpiste | 2 PHYSICAL INPUTS | 0.0 | 10 | -50.0 | 120.0 | °C | ReadOnly | FALSE |
| 22 | TE10_M | Lämpötilamittaus, tuloilma | 2 PHYSICAL INPUTS | 0.0 | 10 | -50.0 | 120.0 | °C | ReadOnly | FALSE |
| 23 | TE31_M | Lämpötilamittaus, jäteilma | 2 PHYSICAL INPUTS | 0.0 | 10 | -50.0 | 120.0 | °C | ReadOnly | FALSE |
| 24 | TE30_M | Lämpötilamittaus, poistoilma | 2 PHYSICAL INPUTS | 0.0 | 10 | -50.0 | 120.0 | °C | ReadOnly | FALSE |
| 25 | ME05_M | Kosteusmittaus, LTO-laite | 2 PHYSICAL INPUTS | 0 | 1 | 0 | 100 | % | ReadOnly | FALSE |
| 26 | QE05_M | Hiilidioksidimittaus, poistoilma | 2 PHYSICAL INPUTS | 0 | 1 | -1 | 2000 | ppm | ReadOnly | FALSE |
| 27 | TF10_I | Indikointi, tulopuhallin | 2 PHYSICAL INPUTS | 0 | 1 | 0 | 1 | | ReadOnly | FALSE |
| 28 | PF30_I | Indikointi, poistopuhallin | 2 PHYSICAL INPUTS | 0 | 1 | 0 | 1 | | ReadOnly | FALSE |
| 29 | ME20_M | Kosteusmittaus, kosteata tila | 2 PHYSICAL INPUTS | 0 | 1 | -1 | 100 | % | ReadOnly | FALSE |
| 30 | QE20_M | Hiilidioksidimittaus, sisäilma | 2 PHYSICAL INPUTS | 0 | 1 | -1 | 2000 | ppm | ReadOnly | FALSE |
| 31 | EXTERNAL_M | Ulkoinen ohjaussignaali (0-10V) | 2 PHYSICAL INPUTS | 0.0 | 10 | -1.0 | 100.0 | % | ReadOnly | FALSE |
| 35 | EXTERNAL_BOOST_M | Ulkoinen tehostussignaali (1-10V) | 2 PHYSICAL INPUTS | 0.0 | 10 | -1.0 | 100.0 | % | ReadOnly | FALSE |
| 36 | TE10_DEFECTION_M | Tulolämpötilan poikkeutus (+/- 3 astetta), (-9.9=EI käytössä) | 2 PHYSICAL INPUTS | 0.0 | 10 | -9.9 | 3.0 | °C | ReadOnly | FALSE |

## 3 PHYSICAL OUTPUTS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 40 | TF10_Y | Säätö, tulopuhallin | 3 PHYSICAL OUTPUTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 42 | PF30_Y | Säätö, poistopuhallin | 3 PHYSICAL OUTPUTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 44 | TV45_Y | Säätö, jälkilämmityspatteri | 3 PHYSICAL OUTPUTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 46 | FG50_Y | Säätö, LTO | 3 PHYSICAL OUTPUTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 48 | EC05_Y | Säätö, esilämmityspatteri | 3 PHYSICAL OUTPUTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 50 | HP_RAD_O | Ohjaus, maalämpömoduli | 3 PHYSICAL OUTPUTS | 0 | 1 | 0 | 1 | | ReadOnly | FALSE |

## 4 SETTINGS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 60 | HOME_SPEED_S | Asetusarvo, Ilmanvaihtoasetus kotona-tilassa | 4 SETTINGS | 3 | 1 | 1 | 5 | | ReadWrite | FALSE |
| 61 | TE10_MIN_HOME_S | Asetusarvo, Tulolämpötilan minimiarvo kotona-tilassa | 4 SETTINGS | 17.0 | 10 | 10.0 | 28.0 | °C | ReadWrite | FALSE |
| 62 | TE10_CONTROL_MODE_S | Asetusarvo, lämpötilan säätö (ECO, Vakio) | 4 SETTINGS | 0 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 63 | AWAY_SPEED_S | Asetusarvo, Ilmanvaihtoasetus poissatilassa | 4 SETTINGS | 1 | 1 | 1 | 5 | | ReadWrite | FALSE |
| 64 | TE10_MIN_AWAY_S | Asetusarvo, Tulolämpötilan minimiarvo poissa-tilassa | 4 SETTINGS | 15.0 | 10 | 10.0 | 28.0 | °C | ReadWrite | FALSE |
| 65 | BOOST_SETTING_S | Asetusarvo, Tehostuksen nopeusasetus (nopeus 3-5) | 4 SETTINGS | 4 | 1 | 3 | 5 | | ReadWrite | FALSE |
| 68 | OVERP_AMOUNT_S | Asetusarvo, Puhaltimien ylipainetilanteen ylipaineen määrä | 4 SETTINGS | 20 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 70 | TP_ENABLE_S | Asetusarvo, Aikaohjelmakäyttö (0=ei käytössä, 1=käytössä) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 71 | AUTO_SUMMER_COOL_S | Asetus, Kesäviilennystoiminto (0=ei käytössä, 1=on, 2=automaatti) | 4 SETTINGS | 2 | 1 | 0 | 2 | | ReadWrite | FALSE |
| 72 | AUTO_SUMMER_POWER_S | Asetus, Kesäkäytön tehomuutokset (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 73 | TE30_S | Asetusarvo, Poistolämpötila (Tavoiteltava huonelämpötila kesäkaudella) | 4 SETTINGS | 18.0 | 10 | 15.0 | 25.0 | °C | ReadWrite | FALSE |
| 74 | AUTO_HEATER_ENABLE_S | Asetus, Jälkilämmitysvastus (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 75 | AUTO_COLD_LOWSPEED_S | Asetus, Automaattinen tehonpudotus kylmissä olosuhteissa (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 76 | COLD_LOWSPEED_S | Asetus, Tehonpudostus pakkasella, pakkasraja | 4 SETTINGS | -15.0 | 10 | -25.0 | 10.0 | °C | ReadWrite | FALSE |
| 77 | AUTO_HUMIDITY_BOOST_S | Asetus, Automaattinen kosteustehostus (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 78 | ME05_BOOST_SENSITIVITY | Asetusarvo, kosteustehostuksen herkkyys | 4 SETTINGS | 1 | 1 | 0 | 2 | | ReadWrite | FALSE |
| 79 | ME_BST_TE01_LIMIT | Asetusarvo, Kosteustehostuksen ulkolämpötilaraja | 4 SETTINGS | -10.0 | 10 | -15.0 | 15.0 | °C | ReadWrite | FALSE |
| 80 | AUTO_CO2_BOOST_S | Asetus, Automaattinen hiilidioksiditehostus (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 81 | AUTO_HOMEAWAY_S | Asetus, Automaattinen kotona/poissa (CO2) (0=ei käytössä, 1=automaatti) | 4 SETTINGS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 82 | QE_HOME_S | Asetusarvo, CO2 kotona-raja | 4 SETTINGS | 500 | 1 | 100 | 2000 | ppm | ReadWrite | FALSE |
| 83 | QE_BOOST_S | Asetusarvo, CO2 tehostusraja (tehostuksen aloitus) | 4 SETTINGS | 800 | 1 | 100 | 2000 | ppm | ReadWrite | FALSE |
| 90 | FILTER_INTERVAL_S | Asetusarvo, Suodattimien vaihtoväli (0=3kk, 1=4kk, 2=6kk) | 4 SETTINGS | 0 | 1 | 0 | 2 | | ReadWrite | FALSE |
| 91 | HP_RAD_MODE | Asetusarvo, maalämpömoduulin toiminta (0=Off, 1=On, 2=Auto) | 4 SETTINGS | 2 | 1 | 0 | 2 | | ReadWrite | FALSE |
| 92 | HP_RAD_WINTER | Asetusarvo, maalämpömoduulin käyttöraja talvi | 4 SETTINGS | 0.0 | 10 | -30.0 | 15.0 | °C | ReadWrite | FALSE |
| 93 | HP_RAD_SUMMER | Asetusarvo, maalämpömoduulin käyttöraja kesä | 4 SETTINGS | 15.0 | 10 | 0.0 | 40.0 | °C | ReadWrite | FALSE |
| 94 | HEATING_SEASON_AVERAGE | Asetusarvo, Lämmityskausi (24h raitis lämpötila) | 4 SETTINGS | 14.0 | 10 | 6.0 | 50.0 | °C | ReadWrite | FALSE |
| 95 | HEATING_SEASON_MOMENT | Asetusarvo, Lämmityskausi (hetkellinen raitis lämpötila) | 4 SETTINGS | 8.0 | 10 | -5.0 | 50.0 | °C | ReadWrite | FALSE |
| 96 | TE10_MIN_SUMMER_S | Asetusarvo, Tulolämpötilan kesä-tilassa | 4 SETTINGS | 12.0 | 10 | 10.0 | 25.0 | °C | ReadWrite | FALSE |
| 97 | TE10_MAX_S | Asetusarvo, Tulolämpötilan maksimiarvo | 4 SETTINGS | 25.0 | 10 | 10.0 | 35.0 | °C | ReadWrite | FALSE |
| 98 | BST_TE01_LIMIT | Asetusarvo, Tehostuksen ulkolämpötilaraja / CO2, 0-10V | 4 SETTINGS | -10.0 | 10 | -15.0 | 0.0 | °C | ReadWrite | FALSE |

## 10 CONFIGURATION PARAMETERS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 105 | M10_TYPE | Mittauspaikan 10 tyyppi. 0=Ei käytössä. | 10 CONFIGURATION PARAMETERS | 0 | 1 | 0 | 27 | | ReadWrite | FALSE |
| 106 | M11_TYPE | Mittauspaikan 11 tyyppi. 0=Ei käytössä. | 10 CONFIGURATION PARAMETERS | 0 | 1 | 0 | 27 | | ReadWrite | FALSE |
| 107 | M12_TYPE | Mittauspaikan 12 tyyppi. 0=Ei käytössä. | 10 CONFIGURATION PARAMETERS | 0 | 1 | 0 | 27 | | ReadWrite | FALSE |
| 108 | SF_SPEED1_S | Asetusarvo, Tulopuhaltimen nopeusasetus 1 | 10 CONFIGURATION PARAMETERS | 20 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 109 | SF_SPEED2_S | Asetusarvo, Tulopuhaltimen nopeusasetus 2 | 10 CONFIGURATION PARAMETERS | 35 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 110 | SF_SPEED3_S | Asetusarvo, Tulopuhaltimen nopeusasetus 3 | 10 CONFIGURATION PARAMETERS | 60 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 111 | SF_SPEED4_S | Asetusarvo, Tulopuhaltimen nopeusasetus 4 | 10 CONFIGURATION PARAMETERS | 75 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 112 | SF_SPEED5_S | Asetusarvo, Tulopuhaltimen nopeusasetus 5 | 10 CONFIGURATION PARAMETERS | 90 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 113 | EF_SPEED1_S | Asetusarvo, Poistopuhaltimen nopeusasetus 1 | 10 CONFIGURATION PARAMETERS | 20 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 114 | EF_SPEED2_S | Asetusarvo, Poistopuhaltimen nopeusasetus 2 | 10 CONFIGURATION PARAMETERS | 35 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 115 | EF_SPEED3_S | Asetusarvo, Poistopuhaltimen nopeusasetus 3 | 10 CONFIGURATION PARAMETERS | 60 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 116 | EF_SPEED4_S | Asetusarvo, Poistopuhaltimen nopeusasetus 4 | 10 CONFIGURATION PARAMETERS | 75 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 117 | EF_SPEED5_S | Asetusarvo, Poistopuhaltimen nopeusasetus 5 | 10 CONFIGURATION PARAMETERS | 90 | 1 | 0 | 100 | % | ReadWrite | FALSE |
| 120 | SENSOR_TE_COR | Lämpötilan korjaus | 10 CONFIGURATION PARAMETERS | 0.0 | 10 | -5.0 | 5.0 | °C | ReadWrite | FALSE |
| 121 | SENSOR_ME_COR | Kosteuden korjaus | 10 CONFIGURATION PARAMETERS | 0 | 1 | -20 | 20 | % | ReadWrite | FALSE |
| 122 | SENSOR_CO2_COR | Hiilidioksidin korjaus | 10 CONFIGURATION PARAMETERS | 0 | 1 | -500 | 500 | ppm | ReadWrite | FALSE |
| 124 | HEATPUMP_RADIATOR_ENABLE | Maalämpöpatteri (0=Ei asennettu, 1=Asennettu) | 10 CONFIGURATION PARAMETERS | 0 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 125 | VENT_MACHINE | IV-koneen tyyppikoodi | 10 CONFIGURATION PARAMETERS | 1 | 1 | -1000 | 1000 | | ReadOnly | FALSE |
| 129 | TE10_MIN_S | Asetusarvo, Tulolämpötilan minimiarvo jonka käyttäjä voi asettaa | 10 CONFIGURATION PARAMETERS | 10.0 | 10 | 10.0 | 25.0 | °C | ReadWrite | FALSE |
| 137 | TE10_BASE_S | Asetusarvo, Tulolämpötilan perusasetusarvo, josta voidaan potikalla poikkeuttaa | 10 CONFIGURATION PARAMETERS | 17.0 | 10 | 15.0 | 25.0 | °C | ReadWrite | FALSE |
| 140 | BST_MINTIME | Asetusarvo, Tehostuksen minimiaika (min) / LTO, CO2, 0-10V | 10 CONFIGURATION PARAMETERS | 5 | 1 | 1 | 60 | min | ReadWrite | FALSE |
| 141 | CO2_MINTIME | Asetusarvo, Automaattinen kotona-poissa minimiaika | 10 CONFIGURATION PARAMETERS | 15 | 1 | 1 | 600 | min | ReadWrite | FALSE |
| 144 | BST_TIME_LIMIT | Asetusarvo, Kosteus ja CO2-tehostusten maksimiaika | 10 CONFIGURATION PARAMETERS | 1440 | 1 | 15 | 1440 | min | ReadWrite | FALSE |


## 6 SOFT MEASUREMENTS AND CONTROL POINTS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 180 | UNIT_CONTROL_FO | IV-koneen ohjaus (0=Off, 1=On) | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 1 | 1 | 0 | 1 | | ReadWrite | FALSE |
| 181 | USERSTATECONTROL_FO | MAC 2 User state control from screen. 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 2 | 1 | 0 | 5 | | ReadWrite | FALSE |
| 182 | DFRST_FI | Fiktiivinen indikointi, LTO:n sulatus päällä/pois | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0 | 1 | 0 | 1 | | ReadOnly | FALSE |
| 183 | FG50_EA_M | Fiktiivinen mittaus, LTO:n hyötysuhde | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 184 | FILTER_STATE_FI | Fiktiivinen asetus, Suodattimen kunto (0=Idle, 1=Kuittaa vaihto, 2=Muistutushälytys) | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0 | 1 | 0 | 2 | | ReadWrite | FALSE |
| 185 | SENSOR_STATUS | Yhdistelmäanturin tila (1=Ok, 0=Initoimatta, -1=Modbuskommunikaatiovirhe, -2=Data puuttuu) | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0 | 1 | -2 | 1 | | ReadOnly | FALSE |
| 189 | SUMMER_MODE_I | Tilatieto, Kausi. 0=Talvi, 1=Väli, 2=Kesä | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0 | 1 | 0 | 2 | | ReadOnly | FALSE |
| 190 | SUMMER_POWER_CHANGE_F | Kesätilanteen tehonsäätö | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0 | 1 | -1 | 1 | | ReadOnly | FALSE |
| 191 | HUMIDITY_FM | Laskettu kosteus | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0.00 | 100 | 0.00 | 100.00 | g/kg | ReadOnly | FALSE |
| 192 | ME05_AVG_FM | Fiktiivinen mittaus, LTO:n kosteusmittauksen 24h keskiarvo | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 199 | PWR_LIMIT_FY | Fiktiivinen säätö, puhaltimien tehonrajoitus | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0.0 | 10 | 0.0 | 100.0 | % | ReadOnly | FALSE |
| 213 | TE01_AVG_FM | Ulkolämpötilan vrk keskiarvo | 6 SOFT MEASUREMENTS AND CONTROL POINTS | 0.0 | 10 | -50.0 | 50.0 | °C | ReadWrite | FALSE |

## 7 ALARMS

| Rekisteri | ID | Kommentti | Ryhmä | Tehdasasetus | Kerroin | MinLimit | MaxLimit | Yksikkö | Käyttöoikeus | Double |
|-----------|-----|-----------|-------|--------------|---------|----------|----------|---------|--------------|--------|
| 220 | TE01_FA | Vikahälytys, raitisilman lämpötila / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 221 | TE10_FA | Vikahälytys, tulolämpötila / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 222 | TE05_FA | Vikahälytys, tulolämpötila LTO:n jälkeen / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 223 | TE30_FA | Vikahälytys, poistolämpötila / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 224 | TE31_FA | Vikahälytys, jäteilman lämpötila / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 225 | ME05_FA | Vikahälytys, LTO:n kosteus / anturivika | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 226 | TF10_CA | Ristiriitahälytys, tulopuhallin | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 227 | PF30_CA | Ristiriitahälytys, poistopuhallin | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 228 | TE10_HA | Ylärajahälytys, tulolämpötila | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 229 | TE30_HA | Ylärajahälytys, poistolämpötila | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 230 | TE10_LA | Alarajahälytys, tulolämpötila | 7 ALARMS | 0 | 1 | 0 | 11 | | ReadOnly | FALSE |
| 240 | FILTER_FA | Suodattimen hälytys | 7 ALARMS | 0 | 1 | 0 | 1 | | ReadOnly | FALSE |

