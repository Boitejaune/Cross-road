# Crossroads

---

Attendu :

Une intersection de 2 route, l'une allant du Nord au Sud et la seconde d'Oeust et Est et vice-versa possèdant 4 feux bicolore (Rouge : stop, Vert : ça roule) à chaque coin. 
Quand une route est au feux vert dans les 2 sens, la route perpendiculaire a les feux en rouge.

Les véhicules réspecte le code de la route, donc les véhicules ne passe que quand le feux est vert, ont la priorité quand ils tournent à droite.
Si il y a une ambulance, police, etc..., elle doit pouvoir passer le plus rapidement qu'importe la situation. Pour cela, le feu vert s'active seulement pour la route où se situe le véhicule. On dira qu'il n'y a pas de véhicule en plein millieu de l'intersection ni de bouchon.

---

Spec technique :

• normal_traffic_gen: Traffic normale, on génère les voitures allant d'une source à une destination de manière aléatoire. (Envoie au coordinator : Source,Destination,Non prioritaire)

• priority_traffic_gen: Présence de véhicule prioritaire et a la priorité. (Envoie au coordinator : Source,Destination,Prioritaire + Envoie un signal aux lights)

• coordinator: Permet à tout les véhicules de rouler selon la régulations du traffique et les feux. (Met les véhicules dans les liste FIFO correspondant à des routes puis updates l'avancé avec les feux)

• lights: Change la couleur des feux à intervalle régulier et s'adapte au véhicule prioritaire. (Espace shared memory) 

• display: Permet de visualiser.

Les 4 premières sections sont représentés par des "message queues", vehicles are represented via messages coding the vehicle’s attributes. Lorsqu'il y a un véhicule prioritaire il envoie un signal au processus "lights". Létats des feux est stocké dans un "shared memory", accessible au process "coordinator". Les communications avec "display" se font pas sockets.

---
Shared resources :
- 1 listes, une pour chaque route avec les voitures au feu
- caractéristiques des voitures (créées par normal_traffic_gen et priotiry_traffic_gen) --> source, dest, position, priorité, mouvement (tout droit, à droite, à gauche) Osef destination du coup ? A gauche doit attendre qu'en face ils soient passés, ou si les deux vont à gauche ça passe ; bloque les autres ? A voir après
- Etat actuel des feux

---
Sémaphore :
Un par route, contient la capacité de passage du nombre de voitures à son feu

---
Logique de la situation :

Vérification de l'état des feux :
La voiture check dans la mémoire partagée si le feu de sa route est vert.
  -> Si le feu est rouge, elle attend (ou ne fait rien jusqu’à ce que le feu soit vert).
  -> Si le feu est vert, la voiture tente d'acquérir le sémaphore de sa route (semaphore[route].acquire()). (Pour garantir qu'elle est autorisée à avancer dans l'intersection sans entrer en conflit avec d'autres voitures.
     Une fois qu'elle a traversé l'intersection, elle libère le sémaphore (semaphore[route].release()).

Si véhicule prio :
Le processus associé envoie un signal au gestionnaire de feux.
Les feux changent immédiatement pour permettre au véhicule prioritaire de passer.
Sémaphores des autres routes temporairement bloqués pour empêcher d'autres voitures d'avancer ?
