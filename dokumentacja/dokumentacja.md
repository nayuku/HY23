# Kryptokasa

# Opis zadania
https://hackyeah.pl/wp-content/uploads/2023/09/DETAILS_Kryptokasa-gov_MF_HackYeah2023.pdf

## Wizja projektu

Strona internetowa, w której użytkownik podaje kryptoaktywa (nazwa, liczba)

Formularz

Umożliwia oszacowanie wartości dla podanego portfelu dla wprowadzonych danych

## Pomysł
Wartość wszystkich kryptoaktywów wyliczona została poprzez zsumowanie uśrednionej wartości kryptoaktywów ze zdefiniowanych źródeł danych.

Podczas uśredniania wartości kryptoaktywa ze wszystkich obsługujących go giełd skorzystano ze średniej arytmetycznej.

Przy pobieraniu informacji o cenie kryptoaktywa z API dostawców zewnętrznych brano pod uwagę ostatnio zanotowaną świeczkę. Preferowano dane wyceniające kryptowalutę do PLN.

## Założenia
Długa nazwa jest unikalna

## Wymagania funkcjonalne
- Automatyczne pobieranie danych wartości kryptowaluty w PLN ($)

- Manualne wprowadzanie danych
- Generowanie raportu

## Pytania
1. Czy musimy ograniczyć się do tylko 1 giełdy (zonda). chcemy wyliczyć faktyczną wartość kryptoaktywa poprzez uśrednienie z wielu giełd (w tym zdecentrtrelizowanym).
2. Czy możemy brac pod uwagę stable coiny (przy wycenie).
1USDT - 1 $ nie zawsze tak jest 0.999
