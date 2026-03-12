Code par Julien GAUTHIER, contact pour des questions : juliengauthier02@gmail.com


Ce code est à destination de l'équipe de Claire Eschbach, réalisé dans le cadre de tracking de larves de drosophiles dans des labyrinthes.

Si jamais vous voulez changer la forme de labyrinthe, utilisez le logiciel GIMP pour obtenir le masque de ce labyrinthe (raccourci b), il faut ensuite colorier chaque chambre du labyrinthe d'une couleur différente pour que le programme sache à quel pixel corresponde chaque salle.

Pour obtenir des masques qui soient compatibles avec les découpes, je recommande de lancer le programme sans l'affichage des masques (voir le fichier main_tracking), faire une capture d'écran de la fenêtre d'un labyrinthe pour lequel vous avez fait une bonne calibration et utiliser cette capture pour faire le détourage.
Cela permet de s'affranchir des considérations d'angle de caméra et de hauteur pour prendre la photo.


Façon dont est réalisée le tracking :
On initialise le centroïde sur le premier contour le plus grand détecté, on cheche ensuite le centroïde le plus proche et on l'assigne.
Des mesures de sécurité sont présentes dans le code pour ne pas faire d'erreurs de tracking :
- On définit une aire maximal et minimale pour le contour détecté, ce qui permet de ne pas considérer de bruit parasite
- On définit une distance max de recherche du nouveau centroïde. Cette distance augmente en fonction du nombre de frames lorsque aucun contour n'est détecté pendant plusieurs frames consécutives
- On met en place la projection d'un masque, ce qui permet de ne garder que les centroïdes qui sont dans ledit masque (attention cependant il faut une bonne calibration)

 