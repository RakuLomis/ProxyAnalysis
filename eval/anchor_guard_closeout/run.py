"""Independent read-only numerical diagnostic; no parent fitting entry points."""
from common import *
import arithmetic
import replay
import summarize
import report

def run():
    if '--preflight' in sys.argv:print(arithmetic.tests(),flush=True);return
    if '--verify' in sys.argv:
        import verify;verify.run();return
    register()
    try:
        write(OUT/'audits/tests.json',arithmetic.tests());replay.run();summarize.run();report.run()
        write(OUT/'read-ledger.json',{'reads':READS,'no_fits':True,'H_U_PCAP_reads':0})
    except Exception as e:
        write(OUT/'failure.json',{'exception':repr(e),'traceback':traceback.format_exc(),'parent_unchanged':True})
        progress('failed',reason=str(e));raise

if __name__=='__main__':run()
