import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import OverviewPage from './pages/OverviewPage';
import PrioritiesPage from './pages/PrioritiesPage';
import SectorPlansPage from './pages/SectorPlansPage';
import GlobalPlanPage from './pages/GlobalPlanPage';
import CommunicationPage from './pages/CommunicationPage';
import SegmentsPage from './pages/SegmentsPage';
import CorpusPage from './pages/CorpusPage';
import AuditPage from './pages/AuditPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/priorities" element={<PrioritiesPage />} />
        <Route path="/sector-plans" element={<SectorPlansPage />} />
        <Route path="/global-plan" element={<GlobalPlanPage />} />
        <Route path="/communication" element={<CommunicationPage />} />
        <Route path="/segments" element={<SegmentsPage />} />
        <Route path="/corpus" element={<CorpusPage />} />
        <Route path="/audit" element={<AuditPage />} />
      </Route>
    </Routes>
  );
}
