# Privacy policy

_Last updated: 24 October 2026. The same text is on [localquench.com/privacy.html](https://localquench.com/privacy.html); Polish below the English._

Local Quench runs on your computer. Your code, chats and keys stay there. This page explains the few cases where personal data does leave it: visiting this website, the app's update checks and web search, and chats you decide to share with us.

## 1. Who is responsible

The controller of personal data described here is Michał Majkowski, ul. Nazaretańska 12, 30-685 Kraków, Poland, e-mail <contact@localquench.com> ("we"). Write to that address for anything about your data. We have not appointed a data protection officer, as the law does not require one for an activity of this size.

## 2. This website

**Server logs.** When you open a page, the hosting provider's server records your IP address, the time, the page requested, the browser's user agent and the referring page. We use these logs only to keep the site running and secure (for example to find attacks or errors). Legal basis: our legitimate interest in a working, secure website (Art. 6(1)(f) GDPR). The hosting provider keeps the logs for a limited time under its own rules (14 days at the time of writing) and then deletes them.

**Cookies and similar.** This website sets no cookies and stores nothing in your browser (no local storage, no tracking pixels, no analytics, no advertising). That is why it shows no cookie banner: there is nothing to consent to. Fonts are served from this server, not from Google or another font service. The model advisor runs entirely in your browser; what you type into it is not sent anywhere.

**E-mail.** If you write to us, we use your address and message to answer and keep the correspondence for as long as needed to handle the matter and possible claims (Art. 6(1)(f) GDPR).

## 3. The Local Quench app

The app processes your projects, chats and settings on your computer. We do not receive them and are not the controller of that data. The app connects to the internet only in these cases:

- **Update checks.** The app asks whether a newer version exists: first our website (localquench.com, whose hosting logs are described in section 2), then GitHub (GitHub, Inc.), and downloads it from GitHub. The same check also fetches the public list of models for the model advisor. GitHub sees your IP address, as with any visit to github.com, under [its own privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). You can turn automatic checks off in Settings; then neither happens.
- **Price list for cloud models.** If you have set up a cloud provider, the app fetches current prices from OpenRouter (OpenRouter, Inc., United States) to show what a chat would cost there. With local models only, it does not.
- **Web search and reading web pages,** only when the agent uses those tools. Searches go to DuckDuckGo, pages are fetched directly from the site in question. Turn the tools off in Settings if you do not want this.
- **Cloud models you connect yourself** (for example Anthropic, OpenAI, Google, OpenRouter, NVIDIA). Your prompts and code then go to that provider under your own account and its terms. We are not part of that relationship and see nothing of it.
- **Phone access** works in one of two ways you choose. Over Tailscale between your own devices: no server of ours is involved, and Tailscale's own privacy policy covers its coordination service. Or directly (WebRTC): the phone and the computer connect to each other over the internet, encrypted end to end. To find each other they leave a few short messages in a mailbox on our server; these are encrypted with a key only your two devices have, so we cannot read them, and they are deleted when picked up or after 5 minutes at most. To keep the mailbox from being flooded, the server counts requests per address for a few minutes, using only a scrambled form of the IP address that changes daily; nothing is logged. To learn their public address, the devices ask public STUN servers (by default Google's and Cloudflare's), which see the IP address, as for any internet connection. Your chats, code and files never pass through our server.
- **Chat sharing,** only if you turn it on. See the next section.

GitHub, OpenRouter, DuckDuckGo, Google and Cloudflare (STUN) are companies based in the United States and see your IP address under their own policies, as with any connection to them. Where such a company is certified under the EU-US Data Privacy Framework, that is the basis for the transfer; otherwise the standard contractual clauses in its terms.

## 4. Sharing chats to improve Local Quench

**What.** If you turn sharing on, the app sends us your chats with the agent from that moment on (and earlier ones only if you also tick "Also chats from before I turned it on"): your messages, the model's replies, the tool calls and their output, the model name, harness settings and timings. Before anything leaves your computer, the app removes API keys, tokens, passwords, e-mail addresses and your home folder, and you can see the original next to the redacted version in Settings. The redaction cannot recognise everything: names, company details or personal data inside your code may remain. Do not turn sharing on for projects with personal data of other people or confidential code.

**Identity.** Chats are stored under a random install identifier created by the app. We do not ask for your name or e-mail, and we use your IP address only to deliver the upload, not to identify you. Because a chat can still contain personal data, we treat shared chats as personal data.

**Purpose.** Two purposes, each with its own consent. (a) Improving Local Quench: analysing where models and the harness fail, evaluating changes and building test tasks. (b) Training and evaluating machine learning models, only if you also tick "Also allow training models with my shared chats". Models trained this way may be published (for example as downloadable weights); the chats themselves are not. Without consent (b) your chats are never used to train a model. Chats with a cloud model (for example Claude, GPT or Gemini) are never used to train models, even with consent (b): their providers' terms do not allow it; the app marks them. We do not sell the data and do not give it to other companies for their own purposes. The full sharing terms are shown in the app before you can turn sharing on.

**Legal basis.** Your consent (Art. 6(1)(a) GDPR), given in the app separately for each purpose. Each change (on, off, earlier chats included or not, deletion) is recorded with its time and the version of these terms, on your computer and on our server, so both sides can show what was allowed when.

**Withdrawal and deletion.** You can turn sharing off, or only the permission to train models, at any time in Settings, Data sharing. Without sharing, nothing more is sent; without the training permission, none of your shared chats, earlier ones included, is used in any training that starts afterwards. Withdrawal does not affect what was done lawfully before it. "Delete my shared data" removes everything stored under your install identifier on our server with the next connection, normally within minutes, and in any case within 30 days. A model that has already been trained on your chats cannot have them removed from it; after deletion your chats are not used for any further training.

**How long.** As long as we need them for the purposes above, and no longer than until you delete them or withdraw consent and ask for deletion. At least every three years we review the stored chats and delete those we no longer need. The consent record is kept for as long as we need to prove consent, at most 6 years after the last change: after "Delete my shared data" it is moved to a separate archive together with the deletion request, and the install identifier and time of the deletion are noted in a deletion log kept for the same period, so we can show what was deleted and when.

**Where.** On a server we rent from Hetzner Online GmbH (Industriestr. 25, 91710 Gunzenhausen, Germany) in the European Union, which processes the data only on our instructions under a data processing agreement. We do not transfer shared chats outside the European Economic Area. If that changes for training on rented computers, it will happen only under the safeguards of Chapter V GDPR, and this policy will say so before it applies.

### Benchmark results

Separately from chats, you can add a QuenchBench result to the public leaderboard. The app asks after every finished run and shows exactly what would be sent: the model and its quantization, the model server and its settings (engine and version, KV cache type, sampling settings), your processor, graphics card, memory, the benchmark settings (including any harness switches and the label you gave the run), the app version, when the run started and finished, and the per-task results (pass or fail, time, tokens, speed). No code, chats, file paths or commands. Each result is sent only after you click Share for that run. **Conversations of a run.** In the same dialog you can also tick "Also send the agent's conversations from this run": then the run's chats go with the result, that is the task text, the model's replies and the commands it ran on our task files, scrubbed like any shared chat (keys, tokens and your home folder removed). QuenchBench tasks are ours, so these conversations contain nothing from your projects. They are stored with the result under your install identifier, used to improve the harness and to train and evaluate models (never when the model was a cloud API), never sold, and deleted together with the result. Legal basis: your consent (Art. 6(1)(a) GDPR). Results are stored under your install's random id, published on the leaderboard grouped by model, quantization, KV cache type, graphics card and task selection (a group can be one computer's results), with memory shown only as a range; a run on a cloud API is marked as such and shows no graphics card, and removed with "Delete my shared data".

**Anonymous results, also sold.** QuenchBench and its tasks are ours: every task was written by Local Quench, so a shared result contains only how a model did on our tasks, never your code, your chats, file contents, API keys, passwords or anything from your own projects. We may sell shared results, both as statistics (for example which graphics cards are used with which models and what they reach) and as individual anonymous runs, for example to hardware makers and model developers. Everything we sell is anonymised: no install id, no IP address, no account or user; dates are given only to the month, hardware only as the model names of the parts and memory as a range (for example "RTX 3090, 32-64 GB RAM"), and a single run is sold only when at least five different installs have shared runs of the same model, quantization and graphics card, so that a rare setup cannot point to you. Buyers must agree not to try to identify anyone. Anonymity is a basic rule of Local Quench, not an option. Your consent to share benchmark results covers this use; without it nothing is sent. Data that has been sold anonymously cannot be linked back to you, so "Delete my shared data" removes your results from everything we keep and sell from then on, but not from copies already delivered.

## 5. Your rights

You have the right to access your data and receive a copy, to have it corrected or deleted, to restrict its processing, to data portability, to object to processing based on legitimate interest, and to withdraw consent at any time. Write to <contact@localquench.com>. For shared chats, include your install identifier (shown in Settings, Data sharing), since we have no other way to find your data. Most of this you can also do directly in the app.

You can complain to a data protection authority. In Poland that is the President of the Personal Data Protection Office (Prezes Urzędu Ochrony Danych Osobowych), ul. Stawki 2, 00-193 Warszawa, [uodo.gov.pl](https://uodo.gov.pl). You can also complain in the EU country where you live or work.

## 6. Other points

Giving us personal data is voluntary: the website and the app work fully without sharing. We make no decisions about you based solely on automated processing, including profiling. Sharing is meant for adults; if you are under 16, do not turn it on without a parent's consent.

We will announce changes to this policy on this page and, for chat sharing, in the app before they apply. A change to what shared chats are used for needs your new consent.

<a id="pl"></a>

## Polityka prywatności

Local Quench działa na Twoim komputerze. Twój kod, czaty i klucze zostają na nim. Ta strona opisuje nieliczne sytuacje, w których dane osobowe go opuszczają: wizyta na tej stronie, sprawdzanie aktualizacji i wyszukiwanie w sieci przez aplikację oraz czaty, które sam zdecydujesz się nam udostępnić.

## 1. Administrator

Administratorem danych osobowych opisanych na tej stronie jest Michał Majkowski, ul. Nazaretańska 12, 30-685 Kraków, e-mail <contact@localquench.com> ("my"). W każdej sprawie dotyczącej Twoich danych napisz na ten adres. Nie wyznaczyliśmy inspektora ochrony danych, ponieważ przy działalności tej skali prawo tego nie wymaga.

## 2. Ta strona internetowa

**Logi serwera.** Gdy otwierasz stronę, serwer dostawcy hostingu zapisuje Twój adres IP, czas, otwieraną stronę, identyfikator przeglądarki i stronę, z której przyszedłeś. Używamy tych logów wyłącznie do utrzymania strony i jej bezpieczeństwa (np. do wykrywania ataków i błędów). Podstawa prawna: nasz prawnie uzasadniony interes w działającej i bezpiecznej stronie (art. 6 ust. 1 lit. f RODO). Dostawca hostingu przechowuje logi przez ograniczony czas według własnych zasad (14 dni w chwili pisania), a następnie je usuwa.

**Pliki cookies i podobne technologie.** Ta strona nie ustawia plików cookies i niczego nie zapisuje w Twojej przeglądarce (bez local storage, pikseli śledzących, analityki i reklam). Dlatego nie wyświetla banera cookies: nie ma na co wyrażać zgody. Czcionki są ładowane z tego serwera, nie z Google ani innej usługi. Doradca modeli działa w całości w Twojej przeglądarce; to, co w nim wpiszesz, nigdzie nie jest wysyłane.

**E-mail.** Jeśli do nas napiszesz, używamy Twojego adresu i wiadomości, żeby odpowiedzieć, i przechowujemy korespondencję tak długo, jak to potrzebne do załatwienia sprawy i ewentualnych roszczeń (art. 6 ust. 1 lit. f RODO).

## 3. Aplikacja Local Quench

Aplikacja przetwarza Twoje projekty, czaty i ustawienia na Twoim komputerze. Nie otrzymujemy ich i nie jesteśmy administratorem tych danych. Aplikacja łączy się z internetem tylko w tych przypadkach:

- **Sprawdzanie aktualizacji.** Aplikacja pyta GitHub (GitHub, Inc.), czy jest nowsza wersja, i pobiera ją stamtąd. GitHub widzi Twój adres IP, jak przy każdej wizycie na github.com, zgodnie z [własną polityką prywatności](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). Automatyczne sprawdzanie można wyłączyć w Ustawieniach.
- **Wyszukiwanie w sieci i czytanie stron,** tylko gdy agent używa tych narzędzi. Zapytania trafiają do DuckDuckGo, strony są pobierane bezpośrednio z danej witryny. Jeśli tego nie chcesz, wyłącz te narzędzia w Ustawieniach.
- **Modele w chmurze, które sam podłączysz** (np. Anthropic, OpenAI, Google, OpenRouter, NVIDIA). Twoje polecenia i kod trafiają wtedy do tego dostawcy na Twoim koncie i na jego warunkach. Nie jesteśmy stroną tej relacji i nic z niej nie widzimy.
- **Dostęp z telefonu** działa na jeden z dwóch wybranych przez Ciebie sposobów. Przez Tailscale między Twoimi urządzeniami: nie uczestniczy w tym żaden nasz serwer, a usługę koordynacji Tailscale obejmuje jego własna polityka prywatności. Albo bezpośrednio (WebRTC): telefon i komputer łączą się ze sobą przez internet, z szyfrowaniem od końca do końca. Żeby się odnaleźć, zostawiają kilka krótkich wiadomości w skrzynce na naszym serwerze; są zaszyfrowane kluczem, który mają tylko Twoje dwa urządzenia, więc nie możemy ich odczytać, i są usuwane po odebraniu, najpóźniej po 5 minutach. Aby nikt nie zalał skrzynki, serwer przez kilka minut liczy zapytania z danego adresu, używając tylko przekształconej postaci adresu IP, zmienianej codziennie; niczego nie zapisujemy w dziennikach. Aby poznać swój adres publiczny, urządzenia pytają publiczne serwery STUN (domyślnie Google i Cloudflare), które widzą adres IP jak przy każdym połączeniu z internetem. Twoje czaty, kod i pliki nigdy nie przechodzą przez nasz serwer.
- **Udostępnianie czatów,** tylko jeśli je włączysz. Zobacz następny punkt.

GitHub, DuckDuckGo, Google i Cloudflare (STUN) to firmy z siedzibą w Stanach Zjednoczonych; widzą Twój adres IP na zasadach własnych polityk, jak przy każdym połączeniu z nimi. Jeśli dana firma ma certyfikat w ramach EU-US Data Privacy Framework, jest on podstawą przekazania; w przeciwnym razie standardowe klauzule umowne w jej warunkach.

## 4. Udostępnianie czatów w celu ulepszania Local Quench

**Co.** Jeśli włączysz udostępnianie, aplikacja wysyła nam Twoje czaty z agentem od tej chwili (wcześniejsze tylko wtedy, gdy zaznaczysz też "Also chats from before I turned it on"): Twoje wiadomości, odpowiedzi modelu, wywołania narzędzi i ich wyniki, nazwę modelu, ustawienia harnessu i czasy. Zanim cokolwiek opuści komputer, aplikacja usuwa klucze API, tokeny, hasła, adresy e-mail i ścieżkę folderu domowego, a w Ustawieniach możesz porównać oryginał z wersją po usunięciu. Mechanizm nie rozpozna wszystkiego: imiona, dane firmy czy dane osobowe w kodzie mogą zostać. Nie włączaj udostępniania dla projektów z danymi osobowymi innych osób ani z poufnym kodem.

**Tożsamość.** Czaty są przechowywane pod losowym identyfikatorem instalacji tworzonym przez aplikację. Nie pytamy o imię ani e-mail, a adresu IP używamy tylko do odebrania przesyłki, nie do identyfikacji. Ponieważ czat może mimo to zawierać dane osobowe, traktujemy udostępnione czaty jak dane osobowe.

**Cel.** Dwa cele, każdy z osobną zgodą. (a) Ulepszanie Local Quench: analiza, gdzie zawodzą modele i harness, ocena zmian i tworzenie zadań testowych. (b) Trenowanie i ocena modeli uczenia maszynowego, tylko jeśli zaznaczysz też "Also allow training models with my shared chats". Modele wytrenowane w ten sposób mogą być publikowane (np. jako wagi do pobrania); same czaty nie są publikowane. Bez zgody (b) Twoje czaty nigdy nie są używane do trenowania modeli. Czaty z modelem w chmurze (np. Claude, GPT czy Gemini) nigdy nie są używane do trenowania modeli, nawet przy zgodzie (b): nie pozwalają na to warunki ich dostawców; aplikacja je oznacza. Nie sprzedajemy tych danych i nie przekazujemy ich innym firmom do ich własnych celów. Pełne warunki udostępniania aplikacja pokazuje przed włączeniem udostępniania.

**Podstawa prawna.** Twoja zgoda (art. 6 ust. 1 lit. a RODO), wyrażona w aplikacji osobno dla każdego celu. Każda zmiana (włączenie, wyłączenie, dołączenie wcześniejszych czatów, usunięcie) jest zapisywana z czasem i wersją tych warunków, na Twoim komputerze i na naszym serwerze, żeby obie strony mogły wykazać, na co i kiedy była zgoda.

**Wycofanie zgody i usunięcie.** Udostępnianie, albo tylko zgodę na trenowanie modeli, możesz wyłączyć w każdej chwili w Ustawieniach, Udostępnianie danych. Bez udostępniania nic więcej nie jest wysyłane; bez zgody na trenowanie żaden z Twoich udostępnionych czatów, także wcześniejszych, nie trafi do trenowania rozpoczętego później. Wycofanie zgody nie wpływa na zgodność z prawem przetwarzania sprzed wycofania. "Delete my shared data" kasuje wszystko, co jest zapisane pod Twoim identyfikatorem instalacji na naszym serwerze, przy najbliższym połączeniu, zwykle w ciągu kilku minut, a najpóźniej w ciągu 30 dni. Z modelu, który już został wytrenowany na Twoich czatach, nie da się ich usunąć; po usunięciu Twoje czaty nie są używane do dalszego trenowania.

**Jak długo.** Tak długo, jak są nam potrzebne do opisanych celów, i nie dłużej niż do chwili, gdy je usuniesz albo wycofasz zgodę z prośbą o usunięcie. Co najmniej raz na trzy lata przeglądamy przechowywane czaty i usuwamy te, których już nie potrzebujemy. Zapis zgód przechowujemy tak długo, jak musimy umieć wykazać zgodę, nie dłużej niż 6 lat od ostatniej zmiany.

**Gdzie.** Na serwerze wynajmowanym od Hetzner Online GmbH (Industriestr. 25, 91710 Gunzenhausen, Niemcy) w Unii Europejskiej, który przetwarza dane wyłącznie na nasze polecenie, na podstawie umowy powierzenia przetwarzania. Nie przekazujemy udostępnionych czatów poza Europejski Obszar Gospodarczy. Jeśli zmieni się to w związku z trenowaniem na wynajętych komputerach, nastąpi to wyłącznie z zabezpieczeniami z rozdziału V RODO, a ta polityka poinformuje o tym, zanim zmiana zacznie obowiązywać.

### Wyniki benchmarków

Niezależnie od czatów możesz dodać wynik QuenchBench do publicznego rankingu. Aplikacja pyta po każdym zakończonym biegu i pokazuje dokładnie, co zostanie wysłane: model i jego kwantyzację, serwer modelu i jego ustawienia (silnik i wersja, typ KV cache, ustawienia próbkowania), procesor, kartę graficzną, pamięć, ustawienia benchmarku (w tym przełączniki harnessu i etykietę biegu), wersję aplikacji, czas rozpoczęcia i zakończenia biegu oraz wyniki zadań (zaliczone lub nie, czas, tokeny, prędkość). Bez kodu, czatów, ścieżek plików i poleceń. Każdy wynik wysyłamy dopiero po kliknięciu Share dla danego biegu. **Rozmowy z biegu.** W tym samym oknie możesz też zaznaczyć "Also send the agent's conversations from this run": wtedy razem z wynikiem wysyłane są czaty tego biegu, czyli treść zadania, odpowiedzi modelu i polecenia, które uruchamiał na naszych plikach zadań, oczyszczone jak każdy udostępniony czat (klucze, tokeny i Twój folder domowy są usuwane). Zadania QuenchBench są nasze, więc te rozmowy nie zawierają nic z Twoich projektów. Są przechowywane razem z wynikiem pod identyfikatorem instalacji, służą do ulepszania harnessu oraz trenowania i oceny modeli (nigdy, gdy modelem było API chmurowe), nie są sprzedawane i są usuwane razem z wynikiem. Podstawa prawna: Twoja zgoda (art. 6 ust. 1 lit. a RODO). Wyniki przechowujemy pod losowym identyfikatorem instalacji, publikujemy w rankingu tylko łącznie z innymi wynikami dla tego samego modelu i sprzętu, a usuwamy je razem z resztą po wybraniu "Usuń moje udostępnione dane".

**Anonimowe wyniki, także na sprzedaż.** QuenchBench i jego zadania są nasze: każde zadanie przygotował Local Quench, więc udostępniony wynik zawiera tylko to, jak model poradził sobie z naszymi zadaniami, nigdy Twój kod, czaty, zawartość plików, klucze API, hasła ani nic z Twoich projektów. Udostępnione wyniki możemy sprzedawać, zarówno jako statystyki (np. jakie karty graficzne są używane z jakimi modelami i co osiągają), jak i jako pojedyncze anonimowe biegi, np. producentom sprzętu i twórcom modeli. Wszystko, co sprzedajemy, jest zanonimizowane: bez identyfikatora instalacji, adresu IP, konta czy użytkownika; daty podajemy tylko z dokładnością do miesiąca, sprzęt wyłącznie nazwami modeli podzespołów, a pamięć jako przedział (np. "RTX 3090, 32-64 GB RAM"), a pojedynczy bieg sprzedajemy tylko wtedy, gdy co najmniej pięć różnych instalacji udostępniło biegi tego samego modelu, kwantyzacji i karty graficznej, żeby rzadka konfiguracja nie mogła wskazać Ciebie. Kupujący muszą zobowiązać się, że nie będą próbować nikogo zidentyfikować. Anonimowość jest podstawową zasadą Local Quench, a nie opcją. Twoja zgoda na udostępnianie wyników benchmarków obejmuje to użycie; bez niej nic nie jest wysyłane. Danych sprzedanych anonimowo nie da się powiązać z Tobą, dlatego "Usuń moje udostępnione dane" usuwa Twoje wyniki ze wszystkiego, co od tej chwili przechowujemy i sprzedajemy, ale nie z kopii już przekazanych.

## 5. Twoje prawa

Masz prawo dostępu do swoich danych i otrzymania ich kopii, ich sprostowania lub usunięcia, ograniczenia przetwarzania, przenoszenia danych, sprzeciwu wobec przetwarzania opartego na prawnie uzasadnionym interesie oraz wycofania zgody w dowolnym momencie. Napisz na <contact@localquench.com>. W sprawie udostępnionych czatów podaj identyfikator instalacji (widoczny w Ustawieniach, Udostępnianie danych), bo inaczej nie znajdziemy Twoich danych. Większość z tego możesz też zrobić bezpośrednio w aplikacji.

Możesz wnieść skargę do Prezesa Urzędu Ochrony Danych Osobowych, ul. Stawki 2, 00-193 Warszawa, [uodo.gov.pl](https://uodo.gov.pl), albo do organu nadzorczego w kraju UE, w którym mieszkasz lub pracujesz.

## 6. Pozostałe informacje

Podanie danych jest dobrowolne: strona i aplikacja działają w pełni bez udostępniania. Nie podejmujemy wobec Ciebie decyzji opartych wyłącznie na zautomatyzowanym przetwarzaniu, w tym profilowaniu. Udostępnianie jest przeznaczone dla osób dorosłych; jeśli masz mniej niż 16 lat, nie włączaj go bez zgody rodzica.

O zmianach tej polityki poinformujemy na tej stronie, a w sprawie udostępniania czatów także w aplikacji, zanim zaczną obowiązywać. Zmiana celu wykorzystania udostępnionych czatów wymaga Twojej nowej zgody.
