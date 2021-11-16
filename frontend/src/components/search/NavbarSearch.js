
import React, {useState } from 'react'
import { useRecoilState } from 'recoil';
import { productQueryState } from 'recoil/productRecoil';
import { useHistory } from 'react-router-dom'


const Search = ({handleClick}) =>{
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
        <div className="same-style header-search d-none d-lg-block">
            <button className="search-active" onClick={e => handleClick(e)}>
                <i className="pe-7s-search" />
            </button>
            <div className="search-content">
                <form action="#">
                    <input type="text" placeholder="Search" onChange= { (e) => setWord(e.target.value)} />
                    <button className="button-search"  onClick={searchProduct}>
                        <i className="pe-7s-search" />
                    </button>
                </form>
            </div>
      </div>
    )
}


export default Search;