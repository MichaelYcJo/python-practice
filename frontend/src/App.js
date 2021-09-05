import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { GlobalStyle } from './globalStyles';
import Main from 'components/Main';
import Products from 'components/Products';
import { productData, productDataTwo } from 'components/Products/data';
import Feature from 'components/Feature';
import Footer from 'components/Footer';


function App() {
  return (
    <Router>
      <GlobalStyle />
      <Main />
      <Products heading='Choose your favorite' data={productData} />
      <Feature />
      <Products heading='Recommand for You' data={productDataTwo} />
      <Footer />
    </Router>
  );
}

export default App;
