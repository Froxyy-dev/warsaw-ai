Daję Ci przykład story, które chcemy zaimplementować w aktualnym systemie:

USER: Moja dziewczyna ma pojutrze urodziny. Zorganizuj imprezę na 10 osób.

(Musimy zrobić call do LLMa z promptem: tutaj masz sytuacje, w której masz pomóc uzytkownikowi, zaproponuj plan imprezy, i dopytaj uzytkownika o potrzebne informacje  ktore wykorzystasz podczas dzwonienia np. gdy masz zarezerwowac sale to potrzebujesz nazwiska  numeru telefonu)

AGENT: Tutaj jest przykladowy plan  wyswietlam plan, czy chcesz cos dostasowac czy potiwerdzasz?

USER: Do rezerwacji sali chce dorzucic balony  a tort chce zeby byl w dedykowanej cukierni zrobiony

(Call do llm z aktualnym planem i feedbackiem uzytkownika zeby poprawil i stworzyl plan)

AGENT: oto poprawiony plan  wyswietl plan  czy chcesz cos dostosowac czy potwierdzasz

USER: potwierdzam

Jak chce to wpleść w system. Zobacz sobie klasę information gatherer tam jest opis jak możemy to zrobić wysokopoziomowo. Chcemy tak naprawdę, żeby ten powyższy scenariusz nam wyszedł bo jest to demo na potrzeby hackathonu. 

Flow jest tam zrobione w jaki sposob odnosze sie do tego teraz potrzebuje zintegrowac to z frontendem zebysmy dali rade zebrac od uzytkownika potrzebne informacje