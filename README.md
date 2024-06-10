### Student: Popa Alexandru Vasile
### Grupa 6 Semigrupa 2

##### WETRANSFER LINK:
https://we.tl/t-EtYDdncR9x
GITHUB LINK(trebuie dezarhivat modelele din SI_PROJECT/EXTRACT_ME_HERE MOB si HUD pentru ca a trebuit sa le separ deoarece intreceau limita de pe github de 100Mb)
https://github.com/Voc94/SI_CNN_PROJECT-with-DJANGO
Imaginile de test se afla tot pe github la linkul ^ de sus.
### 0. Abstract

Am dezvoltat 2 modele:
- un model de clasificare a imaginilor folosind arhitectura CNN pentru a distinge între diverse jocuri video. Am antrenat modelul pe un set de date de imagini din 25 de jocuri diferite, obținând o acuratețe de 99,77% pe setul de antrenament și 98,83% pe setul de validare după 24 de epoci(~aprox 8 ore de antrenare).
- un model de segmentare HUD și Mob/Entități din imagini cu League of Legends pentru a distinge hud-ul(ce poate fi diferit) si entitatiile ce contin o bara de viata deasupra capului,mentionez ca am folosit 2 modele de segmentare dar cel pentru mobi nu este prea reusit 
### 1. Introducere

Clasificarea imaginilor și segmentarea semantică sunt modele importante în domeniul computer vision, cu aplicații variate, inclusiv în recunoașterea obiectelor și analiza imaginilor. Acest proiect explorează utilizarea rețelelor neuronale convoluționale (CNN) pentru clasificarea imaginilor de jocuri video și segmentarea semantică pentru detectarea HUD și entități în imagini din jocuri.

### 2. Prezentare set de date

Setul de date conține 1000 de imagini pentru fiecare joc, din care 800 au fost utilizate pentru antrenament și 200 pentru validare. Imaginile provin din 25 de jocuri video populare, precum Red Dead Redemption și Terraria si Elden Ring(best to classify).
Setul de date a fost luat de pe kaggle dar si folosind yt-dlp impreuna cu ffmpeg pentru a "prelua" datele din walktrough-uri with no commentary,dupa care le am dat crop la watermark-ul din dreapta jos
kaggle: https://www.kaggle.com/datasets/aditmagotra/gameplay-images
youtube: (prea multe)
am folosit acest pipe **suuuper** folositor:
`yt-dlp -o - "YOUTUBE-URL" | ffmpeg -i pipe: -vf "fps=1/25" output%d.png`
$$25 jocuri*1000 poze$$
![[Pasted image 20240609224021.png]]
Setul de date pentru segmentare este mult mai mic,continand 115 imagini pentru modelul de mobi:
![[Pasted image 20240609223452.png]]
iar 63 pentru modelul de hud:
![[Pasted image 20240609223511.png]]
amandoua imparite in img si img_masks
### 3. Related Work

Proiectul nostru se bazează pe cercetări anterioare în domeniul rețelelor neuronale convoluționale și aplicării acestora în clasificarea imaginilor. Ne-am inspirat din lucrările lui Krizhevsky et al. (2012) și He et al. (2016) privind arhitecturile CNN și ResNet.
https://www.youtube.com/watch?v=5rD8f1oiuWM
Pentru segmentarea semantică, am utilizat tehnici avansate de segmentare precum cele prezentate de Chen et al. (2018) în lucrările despre DeepLabv3.
https://www.youtube.com/watch?v=Ac20oEYYdMM
### 4. Model 1: Clasificare imagini jocuri video

#### Descriere model

Am utilizat arhitectura ResNet18 pre-antrenată pe ImageNet. Modelul a fost antrenat timp de 24 de epoci folosind optimizatorul Adam și funcția de pierdere categorical cross-entropy. Performanța modelului a fost evaluată pe setul de validare, obținând o acuratețe de 98.89%.

#### Acuratețe

- Acuratețe antrenament: 99.77%
- Acuratețe validare: 98.83%
![[Pasted image 20240609202712.png]]
![[Pasted image 20240609202756.png]]
![[Pasted image 20240609203032.png]]
### Model 2:

Modelul 2 utilizează două modele de segmentare separate pentru a detecta HUD (Head-Up Display) și mobi/entități din imagini de jocuri League of Legends. Ambele modele de segmentare sunt bazate pe arhitectura DeepLabV3 cu backbone ResNet-50. Datele de antrenament au fost generate folosind platforma Supervisely și instrumentul batched smart tool.
##### Modelul de Segmentare HUD
**Performanță**:

- **Pierdere Epocă 25**: 0.0099
- **Acuratețe validare**: 98.93%.
##### Modelul de Segmentare Mob/Entități
- **Pierdere Epocă 18**: 0.0299.
- **Acuratețe validare**: Modelul pentru entități nu funcționează optim și necesită ajustări suplimentare.

![[Pasted image 20240609221745.png]]
![[Pasted image 20240609221905.png]]
![[Pasted image 20240609222907.png]]
### 5. Rezultate

#### Acuratețe
##### Model 1

- Train Loss: 0.0085
- Train Acc: 0.9977
- Val Loss: 0.0374
- Val Acc: 0.9883
##### Model 2

- HUD Train Loss: 0.0099
- HUD Val Acc: 98.93%
- Mob Train Loss: 0.0299
- Mob Val Acc: Suboptimal
#### Exemple
##### Model 1:
- **Pozitiv:** O imagine din Terraria a fost corect clasificată datorită caracteristicilor vizuale distincte, cum ar fi peisajul vibrant si culorile intense lipsite de depth 3D.
- **Negativ:** O imagine din Cyberpunk 2077 a fost greșit clasificată ca fiind din GTA V, probabil din cauza asemănărilor în designul urban și stilul vizual,iar majoritatea imaginilor high quality(>640x360) care folosesc shadere si contin imagini cu natura sunt misclasificate ca fiind din Ghost of Tsushima
##### Model 2:

- **Pozitiv:** Modelul de segmentare HUD a identificat corect elementele HUD din imaginile League of Legends, ceea ce este esențial pentru recunoașterea vizuală în jocurile video.
- **Negativ:** Modelul de segmentare pentru mobi/entități a avut dificultăți în a distinge corect entitățile din imagini, indicând necesitatea unor ajustări suplimentare în antrenarea modelului și în adnotarea datelor.
### 6. Concluzia

Am demonstrat eficiența utilizării CNN pentru clasificarea imaginilor de jocuri video, obținând o acuratețe înaltă pe setul de date de validare. În viitor, ne propunem să extindem acest model pentru a include mai multe categorii și să îmbunătățim robustețea clasificării. Modelul de segmentare necesită îmbunătățiri, în special pentru detecția mobilor/entităților, dar a arătat rezultate promițătoare în detectarea elementelor HUD.