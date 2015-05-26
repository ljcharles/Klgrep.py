#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#indique l'encodage à utiliser
#the first line in my python file is the adress where python is redirecting for run my script
#without to type python ^^
#the command to redirect the python path is  
#export PATH="/usr/bin/env:/home/ljcharles/klgrep:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/bin/python"
#Le python path indique à python quels dossiers il doit prendre en compte pour sa recherche de modules.
#open .bash_profile ouvre le profile bash pour ajouter de manière permanente ma direction au pythonpath 

##############################
# Recherche dans un fichier  #
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
procédure à lancer
début: recherche term2find au sein de file2lookinto
fin: affiche les tranches de log contenant term2find
"""

def analyse_commande(argv):
    #We can use a global variable in other functions by declaring it as global in each function that assigns to it
    global regexopt
    global verbose
    global maxcountopt
    global maxcount
    global isobject
    global counttranches
    global ignorecase
    global modesilencieux
    global nbrtanche
    global file2lookinto
    global term2find
    
    # we give default values to variables
    nbrtanche = 0
    
    #we try tableau_options = hm:cEivq and tableau_arguments = argv
    try:
        tableau_options, tableau_arguments = getopt.getopt(argv, "hm:cEivq", ["help", "max-count=", "counttranches", "regex", "ignore-case", "verbose", "quiet"])
    except getopt.GetoptError, err:
        # else print help information and exit:
        print ("klgrep: option invalide --" + str(err)) # will print something like "option -a not recognized"
        print "Usage: klgrep.py [OPTION]... TERME [FICHIER]..."
        print "Pour en savoir davantage, faites: « klgrep --help »."
        sys.exit(2)
    
    # pour chaque options et valeur dans nom_option
    for nom_option, valeur in tableau_options:
        #si l'option est verbose
        if nom_option  in ("-v", "--verbose"):
            verbose = True
            print "verbose: ", verbose
           
        #sinon si l'option est help
        elif nom_option in ("-h", "--help"):
            helpguideoptions = """Usage: klgrep.py [OPTION]... TERME [FICHIER] ...
Recherche du TERME dans chaque FICHIER ou sur l'entrée standard.
Exemple: klgrep.py -c "bscsresponder" "journal.log"

Sélection et interprétation de l'expression régulière:
  -E, --regex               utiliser le TERME comme expression régulière
  -q, --quiet               afficher seulement le code retour:
                                - 0 s'il a trouvé une tranche contenant l'occurence
                                - 1 sinon
  -i, --ignore-case         ignorer la distinction de la casse

Divers:
  -v, --verbose             afficher des informations de débogage: mode verbeux
  -h, --help                afficher l'aide et quitter

Contrôle de sortie:
  -m, --max-count=N         arrêter après N concordances du TERME rechercher
  -c, --counttranches       afficher seulement le nombre de tranches 
                            contenant le TERME recherché"""
            print '\033[36m***',helpguideoptions,'***\033[37m' #on affiche helpguideoptions et on quitte
            sys.exit()
            
        elif nom_option in ("-m", "--max-count"): #sinon si l'option est maxcount
            try:
                maxcountopt = True
                maxcount = int(valeur) #valeur est obligatoirement un nombre entier
            except:
                print "l'option m ou max-count doit être suivie d'un nombre entier"
                print "Pour en savoir davantage, faites: « klgrep --help »."
            print "maxcount: ", maxcountopt
            
        elif nom_option in ("-i", "--ignore-case"): #sinon si l'option est d'ignorer la majuscule ou la minuscule
            ignorecase=True
            print "ignore-case: ", ignorecase
            
        elif nom_option in ("-E", "--regex"): #sinon si l'option est regex on cherchera term2find comme une expression régulière
            regexopt = True
            print "regexopt: ", regexopt
            
        elif nom_option in ("-c", "--count"): #sinon si l'option est count
            counttranches = True 
            print "counttranches: ", counttranches 
            
        elif nom_option in ("-q", "--quiet"): #on cherche si il y a des tranches
            modesilencieux = True
            print "modesilencieux: ", modesilencieux 
            
        else: #Sinon option n'est pas gérée
            print "Option non gérée (%s)\n Pour en savoir davantage, faites: « klgrep.py --help ».", nom_option

    try:
        print "terme2find: ",tableau_arguments[0]
        term2find = tableau_arguments[0] #we recover term2find
    except:
        print "Vous avez oublié d'entrer le TERME à rechercher"
        print "Pour en savoir davantage, faites: « klgrep --help »."
        guidedemarche = """Veuillez lancer le script de la manière suivante:
    Klgrep.py term2find file2lookinto
    avec:
    term2find est le terme à rechercher
    il ne peut etre qu'un ensemble de  caractère, un ensemble de chiffre,
    ou une expression régulière (avec l'option -E)
    par exemple : something971, 4562152, ^\d{4}\-\d{2}-\d{2}
    file2lookinto est l'adresse complète du fichier avec son extention
    par exemple: (C:\Users\Freshloic\Documents\stage\journal.log)"""
        print '\033[36m***',guidedemarche,'***\033[37m' 
        sys.exit(1)
        
    try:
        print "file2lookinto: ",tableau_arguments[1]
        file2lookinto = tableau_arguments[1] #we recover file2lookinto
    except:
        print "Vous avez oublié d'entrer le nom du fichier"
        print "Pour en savoir davantage, faites: « klgrep --help »."
        guidedemarche = """Veuillez lancer le script de la manière suivante:
    Klgrep.py term2find file2lookinto
    avec:
    term2find est le terme à rechercher
    il ne peut etre qu'un ensemble de  caractère, un ensemble de chiffre,
    ou une expression régulière (avec l'option -E)
    par exemple : something971, 4562152, ^\d{4}\-\d{2}-\d{2}
    file2lookinto est l'adresse complète du fichier avec son extention
    par exemple: (C:\Users\Freshloic\Documents\stage\journal.log)"""
        print '\033[36m***',guidedemarche,'***\033[37m' 
        sys.exit(1)
        
        
def searchinfile(term2find,file2lookinto,countranche):
    
    #gérer une exception
    try:
        #la variable file est égale à l'ouverture du fichier 
        file = open(file2lookinto, "r")
        #tranche is undefined
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
                    c'est a dire là newtranche = date"""
                    
                if regexopt:
                    isobject = re.search(term2find,str(tranche))
                elif ignorecase:
                    isobject = term2find.lower() in tranche.lower()
                else:
                    isobject = term2find in tranche
                
                if isobject:
                    nbrtranche = nbrtranche + 1
                    if modesilencieux or counttranches or maxcountopt:
                        countranche = countranche +1
                        print ""
                    else:
                        print '\033[1;33m------------------------------\033[1;m'
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
            print ""
            if countranche > 0: #...si countranche...
                #...le code retour sera 0
                sys.exit(0)
            #...sinon...
            else:
                #...le code retour sera 1
                sys.exit(1)
        else:
            if nbrtranche == 0:
                print("Le terme " + term2find + " ne figure pas dans le fichier !")
            
        if counttranches:
            if countranche == 0:
                print("Le terme " + term2find + " ne figure pas dans le fichier !")
            else:
                print "Le nombre de tranche contenant ",term2find,"est ",countranche,"."
        
        if maxcountopt:    
            if countranche > maxcount: #si countranche est sup à maxcount qui reprend l'argument...
                print "le nombre maximum de tranche",maxcount,"est atteint" #... we stop
        
        #close the file
        file.close()
    except IOError:
        #affiche un message d'erreur
        print "Erreur le fichier n'a pas pu être ouvert!"
    except EOFError:
        print "Nous sommes a la fin du fichier"
        
    if verbose:
        # création d'un second handler qui va rediriger chaque écriture de log
        # sur la console
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.DEBUG)
        logger.addHandler(steam_handler)


#si le fichier est importer et ceci est considéré comme le main
if __name__ == '__main__':
    print "Le programme c'est bien lancé",'\033[32m[ok]\033[37m'
    #on assigne aux variables une valeur par default
    regexopt=False
    verbose = False
    maxcountopt = False
    nbrtanche = 0
    maxcount = 0
    counttranches = False
    modesilencieux = False
    ignorecase = False
    term2find = None
    file2lookinto= None
    
    
    #lance la fonction analyse_commande
    analyse_commande(sys.argv[1:])
    
    #lance la fonction searchinfile
    searchinfile(term2find, file2lookinto,0)
    
else:
    print "Le programme ne c'est pas lancé",'\033[31m[erreur]\033[37m'
