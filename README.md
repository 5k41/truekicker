truekicker
----------

### Rating system
The score N:M (N>M) is interpreted as a M-fold draw and a N-M-fold win/lose.  
The score N:N is interpreted as a N-fold draw.  
The score 2:2 is interpreted as a twofold win/lose.  
The score 2:1 is interpreted as a draw and a win/lose.  
 
### Usage

Process kicker (table soccer) scores or anything similiar using Microsoft's TrueSkill.

Install trueskill:

    easy_install trueskill
    
Save kicker scores in .csv data files (see **examplestat.csv** in this repo).  
Running

    python truekicker.py
    
will generate player statistics using matplotlib.
