import math
import cPickle
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--errors", "-e", dest="errors",  help="show errors", action="store_true", default=False)
parser.add_option("--fractions", "-f", dest="fractions",  help="show fractions", action="store_true", default=False)
(options, args) = parser.parse_args()

fsum = file(args[0],"rb")
dmy = cPickle.load(fsum) # saved command line arguments
dmy = cPickle.load(fsum) # histogram contents
allCutflowsByLabels = cPickle.load(fsum)

for cfname,cf in allCutflowsByLabels.iteritems():
    print " "
    print "Cut flow ",cfname
    nsamples = len(cf[0]) - 1

    line = " ".ljust(15)
    for i,l in enumerate(cf[0]):
        if i==0:
            line = l.ljust(15)
        else:
            line += 2*" " + l[:13].rjust(13)
    line +=  2*" " + "Total"[:13].rjust(13)
    print line

    cs = (len(cf[0])-1)*[ 0. ]
    es = (len(cf[0])-1)*[ 0. ]
    for row in cf[1:]:
        csum = 0.
        esum = 0.
        line1 = row[0][:15].ljust(15)
        line2 = " ".ljust(15)
        for j,l in enumerate(row[1:]):
            cs[j] = l[0]
            csum += cs[j]
            es[j] = l[1]
            esum += es[j]**2
            line1 += "{0:15.2f}".format(cs[j])
            line2 += ("  +- "+"{0:8.2f}".format(es[j]).strip()).rjust(15)
        line1 += "{0:15.2f}".format(csum)
        line2 += ("  +- "+"{0:8.2f}".format(math.sqrt(esum)).strip()).rjust(15)
        print line1
        if options.errors:
            print line2
        if options.fractions:
            if csum<1.e-6:
                csum = 1.
            line1 = " ".ljust(15)
            for j in range(len(cs)):
                line1 += "{0:7.1f} +-{1:5.1%}".format(100*cs[j]/csum,es[j]/csum)
            print line1
