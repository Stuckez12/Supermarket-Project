import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import AccountSignUp from './pages/AccountSignUp';
import '@assets/styles/input-output.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/account/sign-up" element={<AccountSignUp />} />
      </Routes>
    </Router>
  );
}

export default App;