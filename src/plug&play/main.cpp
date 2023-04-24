#include "helper/database.hpp"
#include "helper/listener.hpp"

int main(int argv, char** argc) {
  Db::init_msg();
  Ip::init_msg();

  bool db_running = true, ip_running = true;

  while (db_running && ip_running) {

  }
  
  return 0;
}