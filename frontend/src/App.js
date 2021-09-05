import React, { useState } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import Navbar from 'components/Navbar'
import Sidebar from 'components/Sidebar'
import Main from 'components/Main';
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
