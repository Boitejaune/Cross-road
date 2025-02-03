# récupère chaque queue de route, PID feux pour les signaux, shared memory array lights
# pour chaque queue, vérif si il y a des véhicules
    # oui : véhicule prio ?
        # oui : envoie un signal à lights
        # non : si feux vert de la shared memory, de la source = n° queue, alors passe
                # sinon bloque