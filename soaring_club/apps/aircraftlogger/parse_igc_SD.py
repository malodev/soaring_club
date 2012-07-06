from glob import glob
import igc

log=open('log.csv','w')
files = glob('/media/FLARM/*.IGC')
for f in files:
     igcFile = open(f, "r")
     print f
     parser = igc.IGCParser(igcFile)
     parser.parse()
     igcFile.close()
     parser.analyze()
     if parser.takeoffFix()["UTC"] and parser.landingFix()["UTC"]:
         log.write('%s,%s,%s,%s\n' %  (f, parser.takeoffFix()["UTC"], parser.landingFix()["UTC"], (parser.landingFix()["UTC"] - parser.takeoffFix()["UTC"]).seconds )  )
     else:
         log.write('%s,%s,%s,%s\n' %  (f, None, None, None ))

