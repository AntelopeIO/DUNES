#include <talk.hpp>

ACTION talk::post( uint64_t id, uint64_t reply_to, eosio::name user, const std::string& content) {
   message_table table{get_self(), 0};

   require_auth(user);

   if (reply_to)
      table.get(reply_to);

   eosio::check(id < 1'000'000'000ull, "user-specified id is too big");

   if (!id)
      id = std::max(table.available_primary_key(), 1'000'000'000ull);

   table.emplace(get_self(), [&](auto& msg) {
      msg.id = id;
      msg.reply_to = reply_to;
      msg.user = user;
      msg.content = content;
   });
}