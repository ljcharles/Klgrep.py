#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#indique l'encodage à utiliser
#the first line in my python file is the adress where python is redirecting for run my script
#without to type python ^^
#the command to redirect the python path is  
#export PATH="/usr/bin/env:/home/ljcharles/klgrep:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/bin/python"
#Le python path indique à python quels dossiers il doit prendre en compte pour sa recherche de modules.
#open .bash_profile ouvre le profile bash pour ajouter de manière permanente ma direction au pythonpath 
#pour donner des doits d'éxécution au fichier on tape chmod +x klgrep.py
#pwd pour obtenir le répertoir courant
#cd pour se déplacer
#history pour l'historique des commandes, !789 pour activer la command 789, ctrl + r raccourci reverse-history  

##############################
# Recherche complete dans    #
# un fichier avec options    #
# -------------------------  #
# Créé : le 11/05/2015       #
# Auteur : Freshloic         #
# Tuteur : Mr BYRAM Miguel   #
##############################

#importer des modules
import sys, re, logging, os.path, getopt
 
from logging.handlers import RotatingFileHandler
 
# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)
 
# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

"""
klgrep.py works the same way classic grep does (tho much more
simplified and with less functionality) but provides all the regular
expression patterns available in Python.
procédure à lancer
début: recherche term2find au sein de file2lookinto
fin: affiche les tranches de log contenant term2find
"""

#fonction help avec helpcomplete et helpreduite
def help():
    if helpcomplete:
        helpguideoptions = """Usage: klgrep.py [-h] [-m {N}] [-c] [-E] [-i] [-H] [-v] [-q] {TERME} {FICHIER}
Recherche du TERME dans le FICHIER.
Exemple: klgrep.py -c "bscsresponder" "journal.log"

Sélection et interprétation de l'expression régulière:
  -E, --regex              utiliser le TERME comme expression régulière
  -q, --quiet              n'affiche rien retourne seulement le code retour:
                             - 0 s'il a trouvé une tranche contenant l'occurence
                             - 1 sinon
  -i, --ignore-case        ignorer la distinction de la casse

Divers:
  -v, --verbose            afficher des informations de débogage: mode verbeux
  -h, --help               afficher l'aide et quitter

Contrôle de sortie:
  -m N, --max-count=N      arrêter après N concordances du TERME rechercher
  -H, --Highlighted        afficher le TERME en couleur
  -c, --counttranches      afficher seulement le nombre de tranches 
                           contenant le TERME recherché"""
        print helpguideoptions #on affiche helpguideoptions... 
        
    else:#si on souhaite avoir l'aide  réduite
        helpreduite = """Usage: klgrep.py [-h] [-m {N}] [-c] [-E] [-i] [-H] [-v] [-q] {TERME} {FICHIER}
    Recherche du TERME dans chaque FICHIER ou sur l'entrée standard.
    Exemple: klgrep.py -c "bscsresponder" "journal.log" 
    "Pour en savoir davantage, faites: « klgrep.py --help »." """
        
        print helpreduite #on affiche helpreduite... 
    #...et on quitte
    sys.exit(2)
    
#fonction analyse_commande qui analyse les termes passer en arguments lors du lancement du programme
def analyse_commande(argv):
    #We can use a global variable in other functions by declaring it as global in each function that assigns to it
    global regexopt
    global verbose
    global helpcomplete
    global maxcountopt
    global maxcount
    global isobject
    global counttranches
    global ignorecase
    global coloropt
    global modesilencieux
    global nbrtanche
    global file2lookinto
    global term2find
    
    # we give default values to variables
    nbrtanche = 0
    
    #we try tableau_options = hm:cEivq and tableau_arguments = argv
    try:
        tableau_options, tableau_arguments = getopt.getopt(argv, "hm:cEiHvq", ["help", "max-count=", "counttranches", "regex", "ignore-case", "Highlighted" "verbose", "quiet"])
    #on intercepte l'erreur relative aux options
    except getopt.GetoptError, err:
        # else print help information and exit:
        print ("klgrep: option invalide --" + str(err)) # will print something like "option -a not recognized"
        helpcomplete = False
        help()
        sys.exit(2)
    
    # pour chaque options et valeur dans nom_option
    for nom_option, valeur in tableau_options:
        #si l'option est verbose
        if nom_option  in ("-v", "--verbose"):
            verbose = True
           
        #sinon si l'option est help
        elif nom_option in ("-h", "--help"):
            helpcomplete = True
            help()
            sys.exit(2)
            
        elif nom_option in ("-m", "--max-count"): #sinon si l'option est maxcount
            try:
                maxcountopt = True
                if valeur > 0:
                    maxcount = int(valeur) #valeur est obligatoirement un nombre entier positif
                else:#si la valeur est négative on affiche un message d'erreur
                    print "l'option m ou max-count doit être suivie d'un nombre entier positif"
                    helpcomplete = False
                    help()
                    sys.exit(2) 
            except:
                print "l'option m ou max-count doit être suivie d'un nombre entier positif"
                helpcomplete = False
                help()
                sys.exit(2)
                
            
        elif nom_option in ("-i", "--ignore-case"): #sinon si l'option est d'ignorer la majuscule ou la minuscule
            ignorecase=True
            
        elif nom_option in ("-H", "--Highlighted"): #sinon si l'option est d'ignorer la majuscule ou la minuscule
            coloropt=True
            
        elif nom_option in ("-E", "--regex"): #sinon si l'option est regex on cherchera term2find comme une expression régulière
            regexopt = True
            
        elif nom_option in ("-c", "--count"): #sinon si l'option est count
            counttranches = True 
            
        elif nom_option in ("-q", "--quiet"): #on cherche si il y a des tranches
            modesilencieux = True
            
        else: #Sinon option n'est pas gérée
            print "Option non gérée (%s)", nom_option
            helpcomplete = False
            help()
            sys.exit(2)

    try:
        term2find = tableau_arguments[0] #we recover term2find dans les argumments donnés par les utilisateurs
    except:
        print "Vous avez oublié d'entrer le TERME à rechercher"
        helpcomplete = False
        help()
        sys.exit(2)
        
    try:
        file2lookinto = tableau_arguments[1] #we recover file2lookinto dans les argumments donnés par les utilisateurs
    except:
        print "Vous avez oublié d'entrer le nom du fichier"
        helpcomplete = False
        help()
        sys.exit(2)
        
#recherche le terme à trouver dans la tranche et le retourne en couleur        
def color(term2find, tranche):
    
    BEGIN_COLOR="\033[1;33m"#début couleur du terme recherché (ici jaune)
    END_COLOR="\033[m"#fin couleur du terme recherché, le texte suivant aura sa couleur d'origine
    
    result = ""
    mot = r"^(.*?)(" + term2find + ")(.*)$(?ms)"
    
    if regexopt:
        if ignorecase:
            mot = r"^(.*?)(" + term2find + ")(.*)$(?msi)" #le i dans msi permet d'ignorer la casse, le ms permet une recherche sur chaque ligne d'un texte
            ismot = re.search(mot, str(tranche)) 
        else:#on a une regex pour rechercher et on ne prends pas en compte la casse
            mot = r"^(.*?)(" + term2find + ")(.*)$(?ms)"
            ismot = re.search(mot, str(tranche))  
    else:#on n'a pas de regex
        if ignorecase:
            noregterm=re.escape(term2find)
            mot = r"^(.*?)(" + noregterm + ")(.*)$(?msi)"
            ismot = re.search(mot, str(tranche))
            # on n'a pas de regex pour rechercher et on ne prends pas en compte la casse
            # re.escape(string) Return string with all non-alphanumerics backslashed; 
            # this is useful if you want to match an arbitrary literal string 
            # that may have regular expression metacharacters in it
        else:
            noregterm=re.escape(term2find)
            mot = r"^(.*?)(" + noregterm + ")(.*)$(?ms)"
            ismot = re.search(mot,str(tranche))
        
    while ismot: #tant que l'on recherche le mot dans la tranche 
        result+= ismot.group(1) + BEGIN_COLOR + ismot.group(2) + END_COLOR #result = result + la tranche partager en 2 groupes (début de tranche + plus terme trouvé)
        tranche = str(ismot.group(3)) #tranche vaut alors le groupe 3 
        ismot = re.search(mot,tranche)# on recherche le mot dans le groupe 3 
                
    return result+tranche #on retourne le résultat plus la tranche ne contenant pas le terme

#maxcountfunct  permet d'afficher le nombre (positif) de tranche voulu par l'utilisateur      
def maxcountfunct():        
    if maxcountopt:    
        if countranche < (maxcount+1): #tant que countranche est inf à maxcount qui reprend l'argument...
            print '\033[1;33m--------------------', countranche, '--------------------\033[1;m'
            print tranche
            
"""
procédure à lancer
début: recherche term2find au sein de file2lookinto
fin: affiche les tranches de log contenant term2find
"""    
def searchinfile(term2find,file2lookinto):
    
    #gérer une exception
    try:
        #la variable file est égale à l'ouverture du fichier 
        file = open(file2lookinto, "r")
        #tranche is undefined
        global tranche
        global countranche
        global coloropt
        tranche = ""
        nbrtranche = 0
        
        #si la taille du fichier is equals to zero so print the file is empty
        if os.path.getsize(file2lookinto) == 0:
            print '\033[31m[Le fichier est vide !]\033[37m'
            logging.warning("Le fichier est vide")
            sys.exit(2)
        
        #Tant qu'il y a des lignes dans le fichier
        while 1 :
            line = file.readline()
            #not line = plus de lignes alors pause 
            if not line: 
                break
            #regular expression de la date
            regexdate = r"^\d{4}\-\d{2}-\d{2}"
                
            #recherche de la date
            isdate = re.search(regexdate,str(line))
                
            #si on trouve une date dans le texte au début d'une ligne
            if isdate:
                """"on affiche la tranche et la ligne de séparation
                    \n permet d'aller à la ligne
                    On écrase la tranche par la ligne 
                    c'est a dire là tranche = date"""
                
                if regexopt:
                    if ignorecase:
                        mot = r"^(.*)(" + term2find + ")(.*)$(?msi)" #le i dans msi permet d'ignorer la casse, le ms permet une recherche sur chaque ligne d'un texte
                        isobject = re.search(mot,str(tranche))
                    else: #sinon on recherche une regex en ne prenant pas en compte la casse
                        isobject = re.search(term2find,str(tranche))
                else: #si on n'utilise pas d'expression regulière = regex
                    if ignorecase:
                        isobject = term2find.lower() in tranche.lower()
                    else: #sinon on recherche term2find en prenant en compte la casse
                        isobject = term2find in tranche
                
                if isobject:
                    nbrtranche += 1
                    countranche += 1
                    if modesilencieux or counttranches:
                        affiche = "vide" #ne pas effacer sinon bug xD permet de ne rien afficher
                    elif maxcountopt:#sinon si on a l'option maxcount
                        maxcountfunct()
                    else:#si on aucune de ces options
                        if coloropt:# si on a l'option couleur
                            print '\033[1;33m--------------------', countranche, '--------------------\033[1;m'
                            print color(term2find,tranche)
                        else:#si on a pas l'option couleur
                            print '\033[1;33m--------------------', countranche, '--------------------\033[1;m'
                            print tranche
                        logger.info("tranchefinal= <" + tranche + ">")
     
                tranche = str(line)
                        
                
            #Sinon on ajoute la ligne à la tranche jusqu'à ce qu'on a isdate encore   
            else:
                """here tranche is equals to the date more the 
                    others lines who not contain a date ^^"""
                tranche = tranche + str(line)
                logger.info("tranche = <" + tranche + ">")
        
        if modesilencieux:
            if countranche > 0 or nbrtanche > 0: #...si countranche ou nbrtanche...
                #...le code retour sera 0
                sys.exit(0)
            #...sinon...
            else:
                #...le code retour sera 1
                sys.exit(1)
        else:# si on a pas le modesilencieux
            if nbrtranche == 0:
                print("Le terme " + term2find + " ne figure pas dans le fichier !")
            
        if counttranches:
            if countranche == 0:
                print("Le terme " + term2find + " ne figure pas dans le fichier !")
            else:#si countranche different de zero
                print countranche
        
        #close the file
        file.close()
    except IOError:
        #affiche un message d'erreur lors de l'ouverture
        print "Erreur le fichier n'a pas pu être ouvert!"
        sys.exit(2)
    except EOFError:#affiche un message d'erreur si on est en fin de fichier
        print "Nous sommes a la fin du fichier"
        sys.exit(2)
        
    if verbose:
        # création d'un second handler qui va rediriger chaque écriture de log
        # sur la console
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.DEBUG)
        logger.addHandler(steam_handler)
        
    if countranche or nbrtanche > 0: #...si countranche ou nbrtanche...
        #...le code retour sera 0
        sys.exit(0)
    #...sinon...
    else:
        #...le code retour sera 1
        sys.exit(1)


#si le fichier est importer et ceci est considéré comme le main
if __name__ == '__main__':
    
    #on assigne aux variables une valeur par default
    regexopt=False
    verbose = False
    maxcountopt = False
    helpcomplete = False
    nbrtanche = 0
    maxcount = 0
    countranche = 0
    counttranches = False
    modesilencieux = False
    ignorecase = False
    term2find = None
    file2lookinto= None
    coloropt = False
    
    
    #lance la fonction analyse_commande
    analyse_commande(sys.argv[1:])
    
    #lance la fonction searchinfile
    searchinfile(term2find, file2lookinto)
    
