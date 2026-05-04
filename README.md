# Projet-CEA-Tracking-Drosophilia
Projet au CEA : "Tracking of animals and modelling of individual decision-making in Drosophila Melanogaster” 

Code par Julien GAUTHIER, contact pour des questions : juliengauthier02@gmail.com


Ce code est à destination de l'équipe de Claire Eschbach, réalisé dans le cadre de tracking de larves de drosophiles dans des labyrinthes.

Si jamais vous voulez changer la forme de labyrinthe, utilisez le logiciel GIMP pour obtenir le masque de ce labyrinthe (raccourci b), il faut ensuite colorier chaque chambre du labyrinthe d'une couleur différente pour que le programme sache à quel pixel corresponde chaque salle.
Veuillez à détourer une forme plus grande que celle du labyrinthe pour éviter que la larve soit mal détectée par la suite.
Vous devrez ensuite modifier la fonction 'Decoupe_maze' dans 'Calibration.py' pour choisir comment découper votre vidéo.
Le reste du code pourra rester inchangé.

Pour obtenir des masques qui soient compatibles avec les découpes, je recommande de lancer le programme sans l'affichage des masques (voir le fichier main_tracking), faire une capture d'écran de la fenêtre d'un labyrinthe pour lequel vous avez fait une bonne calibration et utiliser cette capture pour faire le détourage.
Cela permet de s'affranchir des considérations d'angle de caméra et de hauteur pour prendre la photo.




Pour réaliser la calibration, il vous faut cliquer sur le bord bas-droit, bas-gauche, haut-gauche puis haut-droit.
Attention à bien respecter l'ordre ou les noms de fichiers seront mélangés.
Vous pouvez toujours recommencer la calibration d'un labyrinthe en appuyant sur "r".





Façon dont est réalisée le tracking :
On initialise le centroïde sur le premier contour le plus grand détecté, on cheche ensuite le centroïde le plus proche et on l'assigne.
Des mesures de sécurité sont présentes dans le code pour ne pas faire d'erreurs de tracking :
- On définit une aire maximal et minimale pour le contour détecté, ce qui permet de ne pas considérer de bruit parasite
- On définit une distance max de recherche du nouveau centroïde. Cette distance augmente en fonction du nombre de frames lorsque aucun contour n'est détecté pendant plusieurs frames consécutives
- On met en place la projection d'un masque, ce qui permet de ne garder que les centroïdes qui sont dans ledit masque (attention cependant il faut une bonne calibration)

Si jamais pendant le tracking vous voyez que l'algorithme n'arrive pas à suivre la larve, appuyez sur 'q', cela annulera le tracking et empêchera ce résultat d'être pris en compte dans des analyses futures.






Vérification et Validation :
- Visualisation de la trajectoire et comparaison entre vidéo et trajectoire calculée
- Visualisation des vitesses et comparaison avec les vitesses "perçues" dans les vidéos
- Dans "Data_Analysis", visualisation des différentes transitions entre chambres et comparaison à la vidéo
- Dans "Data_Analysis_all", visualisation des différentes transitions entre chambres et comparaison à la vidéo
- Dans "Data_analysis_all", Utilisation d'un seul fichier (Experiment_2_20032026/Video/Mazes/Maze_A/Maze_A_top) visualisation des temps dans chaque chambre et comparaison avec les vidéos
- Dans "Data_analysis_all", Utilisation d'un seul fichier (Experiment_1_18032026/Video/Mazes/Maze_A/Maze_A_top) et comparaison des résultats avec ce que donne "Data_analysis".





Trucs utiles :
Pour que le programme fonctionne, il faut que les vidéos soient rangées dans les bons dossiers, avec les noms correspondants.
Pour cela, veuillez simplement placer les vidéos à analyser dans le dossier "Data" puis lancez le fichier "Order_folders.py" dans le dossier Utils.
Cela ordonnera automatiquement les vidéos dans les bons dossiers.
Vous pourrez ensuite lancer "Main.py".


Pour réaliser l'analyse des données, vous avez accès à deux fichiers dans "Data_analysis".
"Data_analysis_all.ipynb" permet de traiter plusieurs fichiers json en même temps.
"Data_analysis.ipynb" permet de traiter un unique fichier json

Le fichier "Data_analysis_all.ipynb" a été grossièrement modifié pour que vous n'ayiez à lancer que quelques cases du notebook.
Une version plus détaillé est dans le dossier 'Utils'.
De même pour "Data_analysis.py".
