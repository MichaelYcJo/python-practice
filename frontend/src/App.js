import React, { useState } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import Navbar from 'screens/Navbar'
import Sidebar from 'screens/Sidebar'
import Main from 'screens/Main';
import { GlobalStyle } from 'globalStyles';




function App() {

  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => {
    setIsOpen(!isOpen);
  }
  return (
    <>
      <Router>
        <GlobalStyle />
        <Navbar toggle={toggle} />
        <Sidebar isOpen={isOpen} toggle={toggle} />

        <Route path='/' component={Main} exact />
        <Route path='/product' component={Main} exact />
      </Router>

    </>
  );
}

export default App;
