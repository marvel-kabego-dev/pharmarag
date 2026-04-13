import DisclaimerBanner from "./DisclaimerBanner";
import SearchBar from "./SearchBar";

function App(){
    return(
         <div className="min-h-screen bg-blue-950">
            <DisclaimerBanner/>
            <div className="flex flex-col gap-4 max-w-xl mx-auto p-8">
                <SearchBar/>
            </div>
         </div>   
    )
}

export default App