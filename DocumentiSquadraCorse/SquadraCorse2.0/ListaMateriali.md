## Raspberry PI

1. Connesione con i vari moduli 

### Modulo espansione GPIO

![MOdulo espanzione GPIO](https://m.media-amazon.com/images/I/713XlsgYQ5L._AC_SY450_.jpg) 
![Modulo espanzione GPIO2](https://m.media-amazon.com/images/I/71rHqdBTNuL._AC_SY450_.jpg)

[Link amamzon ->](https://www.amazon.it/XTVTX-Morsettiera-Raspberry-Connettore-Espansione/dp/B09XV2VS4M/ref=asc_df_B09XV2VS4M?mcid=18026b72f87c37ae82e1718f8086b7c4&tag=googshopit-21&linkCode=df0&hvadid=700848484305&hvpos=&hvnetw=g&hvrand=15869697105286985835&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9201590&hvtargid=pla-2035819517468&psc=1&hvocijid=15869697105286985835-B09XV2VS4M-&hvexpln=0) Modulo espansione GPIO

### Alimentazione RaspBerry Pi

![Alimentatore](https://m.media-amazon.com/images/I/71Yfj-w-VTL._AC_SY450_.jpg)

[Link Amazon ->](https://www.amazon.it/RUNCCI-YUN-Connettore-terminale-ricarica-trasferimento/dp/B0D5M1P5RH/ref=sr_1_21?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3BXF7KWIB2RIB&dib=eyJ2IjoiMSJ9.Ke6kQN7rPmX3hb-utBOVv8PtzsxJ5quOKJTW6APdUZiK3av7zfdPcB0XHL8i0L7lBPEqruf_xJeTZcfqpq7-PNtvHPO6mi3990gIutp2_T-i0Tz483hIgpED2LCHQgUtT33Wo6rU6Y1WdDS26UrcAretYAkc_2DOrqTu1FEbfrl17ihm4ekHuRwHnNDPL42NBe4MhUyBb0-XvajouVS8F6mlst6xrzknyU3ENHjvXQB-Cb4Aicz9b7lY4S7HW7FPdLv71UPzY7Rk5uWZ99s3pQnfQBTgV3I9JpaQ3Pbga1U.981-AQwijv2sTQTJqQSJ277OGt-3fpSo6nkzQTZgVPw&dib_tag=se&keywords=connettore+micro+usb+to+corrente&qid=1765308111&s=pc&sprefix=connetore+micro+usb+to+corrent%2Ccomputers%2C141&sr=1-21) Alimentatore

Pi come già detto per evitare sbalzi di corrente un 

[Link Amazon ->](https://www.amazon.it/Seprendi-commutazione-anti-jamming-schermatura-alimentatore/dp/B0CNPH94XY/ref=asc_df_B0CNPH94XY?mcid=e2ffab72e672334f8e804bd3fd17e517&tag=googshopit-21&linkCode=df0&hvadid=729668464065&hvpos=&hvnetw=g&hvrand=8710854775936708939&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1008236&hvtargid=pla-2451783230598&psc=1&hvocijid=8710854775936708939-B0CNPH94XY-&hvexpln=0) Regolatore corrente AntiJumping 5V

### Collegamento con il computer segnale radio

Ho pensato di usare due moduli LoRa SX127 a 433 MHz con una gittata del segnale molto ampia.

Per la configurazione PC <-> RaspBerry Pi servono:
- 2 moduli LoRa SX1278
- 1 antenne direzionali Yagi 8-14 dBi o 2 antenne collineari 433 MHz 
- 2 cavi RF RG-58 o RG316 m igliore qualità
- 1 raspberry pi 
- 1 USB <-> TTL che fara da adattatore per collegare il modulo aloRa al PC 
- 1 ESP32 (siccome a quanto pare l'antenna no si interfaccia bene con le informazioni)
- Cavi Dupont/fili molto comodi per evitare infinite saldature

Alimentazione 5V 3A per raspberry Pi e 3.3V per il modulo LoRa

Il link sotto è gia il suo.

[Link Amazon](https://www.amazon.it/DUBEUYEW-Principale-ESP32-DevKitC-Sviluppo-ESP32-WROOM-32U/dp/B0D1712P4H/ref=sr_1_5?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3KVDS7S15PRBA&dib=eyJ2IjoiMSJ9._9imb_I4GiHN2Jh9S5cSGOynuZ0FhwZ5GQJ8Zfg176LcVh9nIGi0YOgKFYjkM9KFEpR3kLrckFWjT8g_cH3eyoK7_6rZUA9AKRTS8YbXXPk5-t5Uxt7LDH8RgLZA9o-So_CheYcLPo2kpYpvfYYXaoagm6q0LWKBssjRNBdeM22ssfbXRVAf24M__647XoovV_YsqDd4x2bVlVHXf2IvPws20amXnbtiZNbtUaOQzLOvHf7IuQ-XlUTzBIgftR0c7eBpia5l3nxdVpbmRPnsEWfH3Kdv0JS88YWz4oOne4c.M2Tcd3YP-y4O9XHKDBEIaWfrbzFyRqqaJkqM2tLMG1U&dib_tag=se&keywords=antenna+rf+esp32%2Bdevkitc%2Bv1%2B38%2Bpin&qid=1764928731&sprefix=antenna+rf+esp32%2Bdevkitc%2Bv1%2B38%2Bpin%2Caps%2C55&sr=8-5) ESP 32

[Link Amazon](https://www.amazon.it/SX1278-433MHz-Wireless-Spectrum-Transmission/dp/B07RD2JV7Y/ref=sr_1_2?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=12TIE0DZENNEN&dib=eyJ2IjoiMSJ9.oaocGl7Jf8Hm1u3lNb35EbwzYOArTzZvGBeo7vrOI0pBEfPWwYZYzFrQ-dZdJKwqBbdwuhc1_MfYGz5k1w0Tr1ToaHtR95eqICzUfBGhb3ed5bD7YWiQy0O3pskwCdrea6O9u2Q8_xce2mq3qi7C_5UOXq1mWNntZ5AHFTPjtHHbGmE_x-AJ-OPi-bV2l_Ycu4cBlFv56oyqhBPhUZRzNkQYaQAaO72XntuviZwLviZQBciZKEp395wYvCctZvHAAOBT87Iv8tXBfhl0dBnMhNFrFrNU_X73iDAA6KarR74.a-ELO05uETdOMr6aDYXa2J4wvur24UvukyhYwx13AEY&dib_tag=se&keywords=LoRa+sx1278&qid=1765309796&sprefix=lora+sx1278%2Caps%2C144&sr=8-2) LoRa sx1278 

[Link Amazon](https://www.amazon.it/Iyalezirk-Antenna-impermeabile-Lorawan-prolunga/dp/B0DVQSKTLJ/ref=sr_1_7?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3CSZR1Q2IJHQN&dib=eyJ2IjoiMSJ9.kNWF9-MRhmbE7F2_WdcQHHFdcjVlv35cZiYCgCCcF-ATmhGoHImu3a4srU7XvPC2TPnGtJcO09rL1uTELcmLQzbwJbd02gAdd6gURn3Hm7YW1W0A8_IWbw9luwB9DB19iy5K6bYkcTOa0Fh1C_Vtkf-yDisu2H8v-_q9eEJIYezd-RdMbAp_hdQun4j0GyaSh4_F1fmhvRDUId98ruvoTBshD7usXKNeMWUAcpSbqsXmVuSYqqgxJYJGROR7305VsAPXfXXcBk2gznmIiOIlTM0_XNR3h3oSrtxR3owYTvA.Zjf-EGwZc7LF4HHeF8aJUYqIAx-syQW7E5FC8sPzN-Y&dib_tag=se&keywords=antenna+collineare+433+mhz+5dbi&qid=1765310331&sprefix=antenna+collineare+433+mhz+5+dbi%2Caps%2C145&sr=8-7) Antenne


[Link Amazon](https://www.amazon.it/DSD-TECH-SH-U09C5-convertitore-Supporto/dp/B07WX2DSVB/ref=sr_1_1_sspa?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=7HPLTAIANOU1&dib=eyJ2IjoiMSJ9.hAH0rE1YoY6Rx6GQQn5eWjPHhZ5CXD9kGDUTJKWf5c8xhjHAmSmFB6AJO6XIwtiQLPrCUcoX-FVUMz6Fal9F1TElIGUk8dSlXbDPw9rbpS03S_6PJ8M3eNo3_amgYe_UZsET5YIRDe16QJqdIkiKm7-1tWpRT3goGcxx4zbYu1c16OZ5qof0YNzl9JcWJYooZgcB-CSviedF_sXDh8fYBhgLo-aQsabKECxCc3ZpWd11p1NSG82AgahpwxCXMhk72eS8NpVld72pijJccJ7LQjE9g0GXp_X4Leya_VJvKKA.LzvNRB9TN4izaKSA2pDHkMkUCyr_vWiUPRUYprC2aNY&dib_tag=se&keywords=usb+ttl+5+v&qid=1765310943&sprefix=usb+ttl+5+v%2Caps%2C200&sr=8-1-spons&aref=d6iECTdR23&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1) TTL con cui verra alimentato ESP 32 dal computer

[Link Amazon](https://www.amazon.it/Elegoo-Cavetti-Maschio-Femmina-Raspberry/dp/B01N40EK6M/ref=sr_1_1_sspa?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2LB609W4OQJXM&dib=eyJ2IjoiMSJ9.Ho18E1neXcaIySNlWwtyN3EuzX25u0P14dVzaP4ou7ROZaBEKJeWUQoGKKOfhl5FupNlzXHswsNzB1U0NpQrNQ9Qs8ggUqnkss4-IiMPlhqdfVjEljy_ze5Wvbz71awBu8wopDcFg4MFLiebg4uWn1RMBeoNFdCxNQdmbCW5U9sTkKZyocBTYEoRPMSsKFngEv7qn-foZepNHJD_HbGV33P1rOdlqChjwP5MZmbJz1VhIeVje0_JBOY_yMuvNudhUwSgG7saVBnBSJdNO9VAki8BTZBsr0mZfLuWtYAgbNM.I1Hb4at3U9Q9aPOiub3Bfd4gobkh2ui1zI6aUvIl0kg&dib_tag=se&keywords=cavi+jumper&qid=1765311065&s=electronics&sprefix=cavi+jumper%2Celectronics%2C145&sr=1-1-spons&aref=JbKw29sWJe&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1) Cavi Jumper 120pcs

[Link Amazon](https://www.amazon.it/Boobrie-Cavo-Maschio-Coassiale-RG316/dp/B08PCX8XJJ/ref=sr_1_13?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=20MM1VC8NV07S&dib=eyJ2IjoiMSJ9._oxfFLvLeIdvMfPMSIjbH6w318_7c4L6fgd08YPd9VN-h3QWsb9EBWQ99BdXcvEcY2lw1uedZ9WHn5F3In_vL7a5MIsV6uXibicWYx5NdFygMGYlWBgwofdTIs9kx8fZtYYbeuHal6z3sDtw6AdxkfYB3IhbAvxj4v8R-oNaDIR2fLlkDqP_MIHuzSooiX0x9vQpWbwM-aCzY9P1e8XKJRtJbG3oJla0o7FCdzkaNG6pgq9Yd605rMBU0HFevb-U0M8PlbX_8sl1iB7eg75tal2uNHMVtYAGFISgkrgz1kE.FaEbXak6iQUx8J3cAkuUqA5IsaYHG52cS6NOevmbI6o&dib_tag=se&keywords=cavo%2Brg316&qid=1765311234&sprefix=cavo%2Brg31%2Caps%2C172&sr=8-13&th=1) cavo RG316 15 cm

Quindi l'ESP32 viene collegato al PC tramite TTL 5v  esso si vanno a inviare i dati al LoRa sx1278 a cui è attacata la prima antenna poi il raspberrry pi li riceve tramite il suo modulo LoRa sx1278 anch'esso collegato ad un antenna poi rielabora i dati al suo interno e d eseque le varie azioni

##### Flusso dati completo

1. PC lato utente

    - Il PC invia dati tramite USB a un ESP32 (alimentato a 5 V TTL).

    - L’ESP32 riceve i dati seriali e li prepara per la trasmissione via LoRa.

2. ESP32 → LoRa SX1278

    - L’ESP32 invia i dati al modulo LoRa SX1278 via SPI (alimentazione 3.3 V).

    - Il modulo LoRa modula il segnale e lo trasmette tramite antenna magnetica 433 MHz montata sull’auto.

3. Trasmissione via radio

   - Il segnale viaggia attraverso l’aria fino al lato Raspberry Pi.

4. Raspberry Pi → LoRa SX1278

   - Il modulo LoRa sul Raspberry Pi riceve i pacchetti radio tramite la sua antenna.

    - I dati vengono inviati al Raspberry Pi tramite SPI.

5. Raspberry Pi

    - Riceve, decodifica e rielabora i dati.

    - Esegue le azioni o comandi programmati in base ai dati ricevuti (es. controlli, logging, visualizzazione, ecc.).