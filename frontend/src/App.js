import 'App.scss';
import { BrowserRouter } from 'react-router-dom';
import Root from 'pages'

function App() {
  return (
    <div>
      <BrowserRouter>
        <Root />
      </BrowserRouter>
    </div>
  );
}

export default App;
