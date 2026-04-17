import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1 ml-[260px] min-h-screen flex flex-col">
        <TopBar />
        <main className="flex-1">
          <div className="px-8 pt-7 pb-12 max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
