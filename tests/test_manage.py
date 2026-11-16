import hashlib, importlib.util, io, json, pathlib, sys, tarfile, tempfile, types, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
# fcntl is Linux-only; validation tests also run on non-Linux hosts without installation.
if sys.platform == 'win32': sys.modules['fcntl'] = types.SimpleNamespace()
spec = importlib.util.spec_from_file_location('manage',ROOT/'scripts/manage.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class ArchiveTests(unittest.TestCase):
    def bundle(self,folder,extra=None):
        archive = folder/'test.tar.gz'
        with tarfile.open(archive,'w:gz') as tf:
            files = {'web/index.html':b'<html></html>','runtime/server.py':b'# test','runtime/launch.sh':b'# test','manifest.json':json.dumps({'schema':1}).encode(),'LICENSE':b'fixture','NOTICE.md':b'fixture','source/package-lock.json':b'{}'}
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tf.addfile(info,io.BytesIO(data))
            if extra: tf.addfile(extra)
        sums = folder/'SHA256SUMS'
        sums.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
        target = folder/'extracted'
        target.mkdir()
        return archive,sums,target
    def test_valid(self):
        with tempfile.TemporaryDirectory() as t:
            args = self.bundle(pathlib.Path(t))
            m.validate_archive(*args)
            self.assertTrue((args[2]/'web/index.html').is_file())
    def test_checksum(self):
        with tempfile.TemporaryDirectory() as t:
            a,s,d = self.bundle(pathlib.Path(t))
            a.write_bytes(a.read_bytes()+b'tamper')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch'): m.validate_archive(a,s,d)
    def test_filename(self):
        with tempfile.TemporaryDirectory() as t:
            a,s,d = self.bundle(pathlib.Path(t))
            s.write_text(s.read_text().replace('test.tar.gz','other.tar.gz'))
            with self.assertRaises(ValueError): m.validate_archive(a,s,d)
    def test_traversal(self):
        for name in ['../escape','/absolute','a/../../escape','C:/escape','a\\escape']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as t:
                args = self.bundle(pathlib.Path(t),tarfile.TarInfo(name))
                with self.assertRaises(ValueError): m.validate_archive(*args)
    def test_links_and_special_files(self):
        for kind in [tarfile.SYMTYPE,tarfile.LNKTYPE,tarfile.FIFOTYPE,tarfile.CHRTYPE]:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as t:
                member = tarfile.TarInfo('web/escape')
                member.type = kind
                member.linkname = '../../escape'
                args = self.bundle(pathlib.Path(t),member)
                with self.assertRaises(ValueError): m.validate_archive(*args)
    def test_failed_update_rolls_back(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as t:
            base = pathlib.Path(t)/'installation'
            base.mkdir()
            args = self.bundle(pathlib.Path(t))
            events = []
            def ctl(*a,**kw): events.append(a)
            # Model symlink changes to run this transaction test without Windows symlink privileges.
            with mock.patch.object(m,'BASE',base), mock.patch.object(m,'owned'), mock.patch.object(m.os,'readlink',return_value='releases/old'), mock.patch.object(pathlib.Path,'is_symlink',return_value=True), mock.patch.object(m,'switch') as switch, mock.patch.object(m,'ctl',side_effect=ctl), mock.patch.object(m,'health',side_effect=RuntimeError('failed')):
                with self.assertRaises(RuntimeError): m.activate(args[0],args[1])
                self.assertEqual(switch.call_args.args,('releases/old',))
                self.assertEqual(len(events),2)
    def test_successful_update_retains_previous(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as t:
            base = pathlib.Path(t)/'installation'
            base.mkdir()
            a,s,_ = self.bundle(pathlib.Path(t))
            with mock.patch.object(m,'BASE',base), mock.patch.object(m,'owned'), mock.patch.object(m.os,'readlink',return_value='releases/old'), mock.patch.object(pathlib.Path,'is_symlink',return_value=True), mock.patch.object(m,'switch') as switch, mock.patch.object(m,'ctl'), mock.patch.object(m,'health'):
                m.activate(a,s)
                self.assertTrue(switch.call_args.args[0].startswith('releases/'))
                self.assertEqual((base/'previous').read_text(),'releases/old')
    def test_uninstall_preserves_unrelated_files(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as t:
            home = pathlib.Path(t)
            base = home/'.local/share/betaflight-uconsole'
            base.mkdir(parents=True)
            (base/m.MARKER).touch()
            unrelated = home/'keep.txt'
            unrelated.write_text('keep')
            unit = home/'test.service'
            unit.touch()
            desktop = home/'test.desktop'
            desktop.touch()
            with mock.patch.object(m,'HOME',home), mock.patch.object(m,'BASE',base), mock.patch.object(m,'UNIT',unit), mock.patch.object(m,'DESKTOP',desktop), mock.patch.object(m,'ctl'), mock.patch.object(m.os,'geteuid',return_value=1000,create=True), mock.patch.multiple(m.fcntl,flock=lambda *a:None,LOCK_EX=1,LOCK_NB=2,create=True), mock.patch.object(sys,'argv',['manage.py','uninstall']):
                m.main()
            self.assertFalse(base.exists())
            self.assertTrue(unrelated.is_file())
            self.assertFalse(unit.exists())
            self.assertFalse(desktop.exists())
if __name__ == '__main__': unittest.main()
