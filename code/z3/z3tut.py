from z3 import *
## look at z3.py

## Satisfiability
x = Int('x')
y = Int('y')
s = Solver()
s.add(x + y > 0)
print s.check()
print s.model()

print s.model()[x]
print s.model()[y]

s.reset()

# Unsatisfiable example
s.add(And(x + y > x, y < 0))
print s.check()

##############################
# Checking implication A => B
# VALIDITY
A = x > 0
B = x > -10

s.add(A)
s.add(Not(B))

if  s.check() == unsat:
    print "VALID"
else:
    print "NOT VALID"

def isValid(phi):
    s = Solver()
    s.add (Not(phi))
    if s.check() == sat:
        print s.model()
        return False
    else:
        return True

#############################
# Bools

p = Bool('p')
q = Bool('q')
r = Bool('r')

s = Solver()
s.add(And(Or(p,q), Implies(q,r)))
print s.check()
m = s.model()
print m

# negate the model
phi = True
s.add(p != m[p])
s.add(q != m[q])
s.add(r != m[r])
print s.check()
m = s.model()
print m

s.add(p != m[p])
s.add(q != m[q])
s.add(r != m[r])

print s.check()

############################
# checking Hoare triples

# {x > 0} x <- x + 1 {x > 1}

x = Int('x')
x1 = Int('x1')

pre = x > 0
trans = x1 == x + 1
post = x1 > 1

print isValid(Implies(And(pre, trans), post))

# {x > 0} x <- x + y {x > 1}

y = Int('y')
y1 = Int('y1')

pre = x > 0
trans = And(x1 == x + y, y1 == y)
post = x1 > 1

print isValid(Implies(And(pre, trans), post))

 
# {LOCK == 0 /\ new != old}
# while (new != old)
#   old = new;
#   if (*) {
#       LOCK = 0;
#       new++;
#   }else{
#       LOCK = 1
#{LOCK != 0} 

lock = Int('lock')
lockp = Int('lockp')

old = Int('old')
oldp = Int('oldp')

new = Int('new')
newp = Int('newp')

pre = lock == 0
post = lock != 0

trans = And(oldp == new,
            Or(And(lockp == 0, newp == new + 1),
                And(lock == 1, newp == new)))

loop = new != old

inv = (old != new) == (lock == 0)
invp = (oldp != newp) == (lockp == 0)

print isValid(Implies(And(inv, loop, trans), invp))

exit(1)
############################
# predicate abstraction

def abstract(phi, preds):
    res = And(True)

    for p in preds:
        if isValid(Implies(phi,p)):
            res = And(res,p)
        if isValid(Implies(phi, Not(p))):
            res = And(res, Not(p))

    return simplify(res)


x = Int('x')
y = Int('y')
xp = Int('x\'')
yp = Int('y\'')

varMap = [(x,xp), (y,yp)]
varMapRev = map(lambda v: (v[1], v[0]), varMap)

def inductive(inv,trans):
    invprime = substitute(inv,varMap)
    return isValid(Implies(And(inv,trans), invprime))

init = And(x == 0, y == 0)
trans = And(xp == x + 1, yp == y + 1)
post = Implies (y == 10, x == 10)

# preds = [x > 0]
# preds = [x >= 0]
# preds = [x >= y, x <= y]
# preds = [x == 0, y == 0, y == 1, x == 1, x == 2, y == 2]
predsprime = map(lambda p: substitute(p,*varMap), preds)


inv = abstract(init, preds)

i = 0
while not inductive(inv,trans):
    print "\nInv at ", i, ": ", inv
    i = i + 1

    # existential quantifer??
    onestep = abstract(And(inv, trans), predsprime)
    onestep = substitute(onestep, varMapRev)
    inv = Or(inv, onestep)


print "\n\nFinal inv --> ", simplify(inv)

if isValid(Implies(inv,post)):
    print "SAFE"
else:
    print "UNSAFE"
