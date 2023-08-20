import React, {useState} from "react";
import { useRecoilState } from 'recoil';
import { productQueryState } from 'recoil/productRecoil';
import { useHistory } from 'react-router-dom'


const MobileSearch = () => {
  const [word, setWord] = useState("");
  const [queryState, setQueryState] = useRecoilState(productQueryState);

  let history = useHistory()
  

  const searchProduct = (e) =>{
      e.preventDefault();
      setQueryState(word)
      if (queryState) {
          history.push(`/products/search`)
      } else {
          history.push(history.push(history.location.pathname))
      }

  }
  return (
    <div className="offcanvas-mobile-search-area">
      <form action="#">
        <input type="text" placeholder="Search" onChange= { (e) => setWord(e.target.value)} />
        <button className="button-search"  onClick={searchProduct}>
          <i className="fa fa-search" />
        </button>
      </form>
    </div>
  );
};

export default MobileSearch;
