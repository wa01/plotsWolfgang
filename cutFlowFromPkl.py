import math
import cPickle
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--noyields", dest="noyields",  help="suppress yields", action="store_true", default=False)
parser.add_option("--errors", "-e", dest="errors",  help="show errors", action="store_true", default=False)
parser.add_option("--fractions", "-f", dest="fractions",  help="show fractions", action="store_true", default=False)
(options, args) = parser.parse_args()
if options.noyields:
    options.errors = False
    options.fractions = True

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
        hdr = row[0][:15]
        if not options.noyields:
            line1 = hdr.ljust(15)
            hdr = " "
        if options.errors:
            line2 = hdr.ljust(15)
            hdr = " "
        for j,l in enumerate(row[1:]):
            cs[j] = l[0]
            csum += cs[j]
            es[j] = l[1]
            esum += es[j]**2
            if not options.noyields:
                line1 += "{0:15.2f}".format(cs[j])
            if options.errors:
                line2 += ("  +- "+"{0:8.2f}".format(es[j]).strip()).rjust(15)
        if not options.noyields:
            line1 += "{0:15.2f}".format(csum)
            print line1
        if options.errors:
            line2 += ("  +- "+"{0:8.2f}".format(math.sqrt(esum)).strip()).rjust(15)
            print line2
        if options.fractions:
            if csum<1.e-6:
                csum = 1.
            line1 = hdr.ljust(15)
            for j in range(len(cs)):
                line1 += "{0:7.1f} +-{1:5.1%}".format(100*cs[j]/csum,es[j]/csum)
            print line1
